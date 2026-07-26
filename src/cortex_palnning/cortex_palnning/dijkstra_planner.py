#!/usr/bin/env python3

# ============================
# ROS2 Libraries
# ============================
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy

# Messages
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import Pose, PoseStamped

# TF
from tf2_ros import Buffer, TransformListener, LookupException

# Priority Queue used by Dijkstra
from queue import PriorityQueue


# =====================================================
# Graph Node
# Represents one grid cell used by the planner.
# =====================================================
class GraphNode:

    # Initialize node position, accumulated cost and parent.
    def __init__(self, x, y, cost=0, prev=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.prev = prev

    # Compare nodes by cost (used by PriorityQueue).
    def __lt__(self, other):
        return self.cost < other.cost

    # Two nodes are equal if they represent the same grid cell.
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Allow GraphNode to be stored inside a set().
    def __hash__(self):
        return hash((self.x, self.y))

    # Create a neighboring node using (dx, dy).
    def __add__(self, other):
        return GraphNode(self.x + other[0], self.y + other[1])


# =====================================================
# Dijkstra Planner Node
# =====================================================
class DijkstraPlanner(Node):

    def __init__(self):
        super().__init__("dijkstra_planner")

        # -----------------------------------------
        # Planner Inputs
        # Map + Goal Pose + Robot Pose (TF)
        # -----------------------------------------

        # Latched QoS so late subscribers still receive the latest map.
        self.qos = QoSProfile(depth=10)
        self.qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        # Receive OccupancyGrid
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            "/map",
            self.map_callback,
            self.qos,
        )

        # Receive goal selected in RViz
        self.goal_sub = self.create_subscription(
            PoseStamped,
            "/goal_pose",
            self.goal_callback,
            10,
        )

        # TF buffer stores transforms.
        # Listener continuously fills the buffer.
        self.buffer_tf = Buffer()
        self.listener_tf = TransformListener(self.buffer_tf, self)

        # -----------------------------------------
        # Planner Outputs
        # -----------------------------------------

        # Publish shortest path
        self.path_pub = self.create_publisher(
            Path,
            "/dijkstra/path",
            10,
        )

        # Publish visited cells for visualization
        self.map_pub = self.create_publisher(
            OccupancyGrid,
            "/dijkstra/visited_map",
            10,
        )

        # Store received map
        self.map_ = None

        # Map used only to visualize visited cells
        self.visited_map = OccupancyGrid()

    # =====================================================
    # Receive Occupancy Grid
    # =====================================================
    def map_callback(self, map: OccupancyGrid):

        # Save latest map.
        self.map_ = map

        # Initialize empty visualization map.
        self.visited_map.header.frame_id = map.header.frame_id
        self.visited_map.info = map.info
        self.visited_map.data = [-1] * (map.info.width * map.info.height)

    # =====================================================
    # Receive Goal Pose
    # =====================================================
    def goal_callback(self, goal: PoseStamped):

        # Cannot plan without a map.
        if self.map_ is None:
            self.get_logger().error("No map received!")
            return

        # Get robot pose in the map frame using TF.
        try:
            map_to_base_tf = self.buffer_tf.lookup_transform(
                self.map_.header.frame_id,
                "base_footprint",
                rclpy.time.Time(),
            )

        except LookupException:
            self.get_logger().error(
                "Could not transform from map to base_footprint"
            )
            return

        # Convert TF transform into Pose.
        map_to_base_pose = Pose()

        map_to_base_pose.position.x = map_to_base_tf.transform.translation.x
        map_to_base_pose.position.y = map_to_base_tf.transform.translation.y
        map_to_base_pose.orientation = map_to_base_tf.transform.rotation

        # Run Dijkstra.
        path = self.plan(map_to_base_pose, goal.pose)

        # Publish path if one exists.
        if path.poses:
            self.get_logger().info("Shortest path found!")
            self.path_pub.publish(path)
        else:
            self.get_logger().warn("No path found to the goal.")

    # =====================================================
    # Dijkstra Planner
    # =====================================================
    def plan(self, start: Pose, goal: Pose):

        # Four-connected grid.
        explore_directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

        # -----------------------------------------
        # Initialize Search
        # -----------------------------------------

        # Open list (waiting nodes).
        pending_nodes = PriorityQueue()

        # Closed list (visited nodes).
        visited_nodes = set()

        # Convert robot pose into grid coordinates.
        start_node = self.world_to_grid(start)
        goal_node = self.world_to_grid(goal)
        # Insert start node.
        pending_nodes.put(start_node)

        # -----------------------------------------
        # Main Search Loop
        # -----------------------------------------
        while not pending_nodes.empty() and rclpy.ok():

            # Expand lowest-cost node.
            active_node = pending_nodes.get()

            # Stop when goal is reached.
            if active_node == goal_node:
                break

            # Explore neighboring cells.
            for x_dir, y_dir in explore_directions:

                # Generate neighbor.
                new_node: GraphNode = active_node + (x_dir, y_dir)

                # Check map bounds, obstacles and visited nodes.
                if (
                    new_node not in visited_nodes
                    and self.pose_on_map(new_node)
                    and self.map_.data[self.pose_to_cell(new_node)] == 0
                ):

                    # Update accumulated cost.
                    new_node.cost = active_node.cost + 1

                    # Save parent for path reconstruction.
                    new_node.prev = active_node

                    # Add neighbor to open list.
                    pending_nodes.put(new_node)

                    # Mark node as discovered.
                    visited_nodes.add(new_node)

            # Color expanded node for RViz visualization.
            self.visited_map.data[self.pose_to_cell(active_node)] = 10
            self.map_pub.publish(self.visited_map)

        # -----------------------------------------
        # Reconstruct Path
        # -----------------------------------------

        path = Path()
        path.header.frame_id = self.map_.header.frame_id

        # Follow parent pointers back to the start.
        while active_node and active_node.prev and rclpy.ok():

            # Convert grid cell into world coordinates.
            last_pose: Pose = self.grid_to_world(active_node)

            last_pose_stamped = PoseStamped()
            last_pose_stamped.header.frame_id = self.map_.header.frame_id
            last_pose_stamped.pose = last_pose

            # Add waypoint.
            path.poses.append(last_pose_stamped)

            # Move to previous node.
            active_node = active_node.prev

        # Reverse because path was built from goal to start.
        path.poses.reverse()

        return path

    # =====================================================
    # Convert World -> Grid
    # =====================================================
    def world_to_grid(self, pose: Pose) -> GraphNode:

        # Convert meters into grid indices.
        grid_x = int(
            (pose.position.x - self.map_.info.origin.position.x)
            / self.map_.info.resolution
        )

        grid_y = int(
            (pose.position.y - self.map_.info.origin.position.y)
            / self.map_.info.resolution
        )

        return GraphNode(grid_x, grid_y)

    # =====================================================
    # Convert Grid -> World
    # =====================================================
    def grid_to_world(self, node: GraphNode) -> Pose:

        pose = Pose()

        # Convert grid indices back into world coordinates.
        pose.position.x = (
            node.x * self.map_.info.resolution
            + self.map_.info.origin.position.x
        )

        pose.position.y = (
            node.y * self.map_.info.resolution
            + self.map_.info.origin.position.y
        )

        return pose

    # =====================================================
    # Check Map Bounds
    # =====================================================
    def pose_on_map(self, node: GraphNode):

        # Verify that the node lies inside the map.
        return (
            0 <= node.x < self.map_.info.width
            and 0 <= node.y < self.map_.info.height
        )

    # =====================================================
    # Convert Grid (x,y) -> 1D Array Index
    # =====================================================
    def pose_to_cell(self, node: GraphNode):

        # OccupancyGrid stores data as a 1D array.
        return node.y * self.map_.info.width + node.x


# =====================================================
# Main
# =====================================================
def main(args=None):

    rclpy.init(args=args)

    node = DijkstraPlanner()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()