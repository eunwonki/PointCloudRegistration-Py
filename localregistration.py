import cv2 as cv
import open3d as o3d
import numpy as np

import util


def open3d_icp(source_node, target_node, initial_transformation, voxel_size):
    source_pcd = util.geom_node_to_pcd(source_node)
    target_pcd = util.geom_node_to_pcd(target_node)

    distance_threshold = voxel_size * 0.4
    print(":: Point-to-plane ICP registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_icp(
        source_pcd, target_pcd, distance_threshold, initial_transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    print(result)
    return result.transformation


def open3d_gicp(source_node, target_node, initial_transformation, voxel_size):
    source_pcd = util.geom_node_to_pcd(source_node)
    target_pcd = util.geom_node_to_pcd(target_node)

    distance_threshold = voxel_size * 0.4
    print(":: gicp registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_generalized_icp(
        source_pcd, target_pcd, distance_threshold, initial_transformation,
        o3d.pipelines.registration.TransformationEstimationForGeneralizedICP())
    print(result)
    return result.transformation


def opencv_icp(source_node, target_node, initial_transformation):
    source_pc = util.geom_node_to_numpy_pc(source_node)
    target_pc = util.geom_node_to_numpy_pc(target_node)

    iterations: int = 100
    tolerence: float = 0.005
    rejectionScale: float = 2.5
    numLevels: int = 8

    print(":: opencv icp registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    icp = cv.ppf_match_3d_ICP(iterations=iterations
                              , tolerence=tolerence
                              , rejectionScale=rejectionScale
                              , numLevels=numLevels
                              , sampleType=0
                              , numMaxCorr=1)

    pose3d = cv.ppf_match_3d_Pose3D()
    pose3d.updatePose(np.array(initial_transformation))

    retval, poses = icp.registerModelToScene(source_pc, target_pc, [pose3d])
    print("   residual: %.6f." % poses[0].residual)

    if poses[0].residual > 1.0:
        return np.eye(4)

    return poses[0].pose


def colored_icp(source_node, target_node, initial_transformation, voxel_size):
    source_pcd = util.geom_node_to_pcd(source_node)
    target_pcd = util.geom_node_to_pcd(target_node)

    print(":: colored icp registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   radius threshold %.3f." % voxel_size)

    result = o3d.pipelines.registration.registration_colored_icp(
        source_pcd, target_pcd, voxel_size, initial_transformation,
        o3d.pipelines.registration.TransformationEstimationForColoredICP(
            lambda_geometric=0.8   # default: 0.968000
        ),
        o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6,
                                                          relative_rmse=1e-6,
                                                          max_iteration=50))
    print(result)

    return result.transformation
