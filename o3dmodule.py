import numpy as np
import open3d as o3d


def read_pointcloud(filename):
    return o3d.io.read_point_cloud(filename)


def read_mesh_to_pointcloud(filename):
    mesh = o3d.io.read_triangle_mesh(filename)
    pcd = o3d.geometry.PointCloud()
    pcd.points = mesh.vertices
    return pcd


def down_sampling(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)
    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))
    return pcd_down


def fpfh(pcd, voxel_size):
    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_fpfh


def global_registration(source, target, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source, target, fpfh(source, voxel_size), fpfh(target, voxel_size), True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result

def local_registration_icp(source, target, initial_transformation, voxel_size):
    distance_threshold = voxel_size * 0.4
    print(":: Point-to-plane ICP registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_icp(
        source, target, distance_threshold, initial_transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    return result

def local_registration_gicp(source, target, initial_transformation, voxel_size):
    distance_threshold = voxel_size * 0.4
    print(":: gicp registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_generalized_icp(
        source, target, distance_threshold, initial_transformation,
        o3d.pipelines.registration.TransformationEstimationForGeneralizedICP())
    return result