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
    source_pc = util.apply_transformation(initial_transformation, source_pc)
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
                              , numLevels=numLevels)

    retval, residual, pose = icp.registerModelToScene(source_pc, target_pc)
    print("   residual: %.6f." % residual)

    if residual > 1.0:
        return np.eye(4)

    return np.matmul(pose, initial_transformation)