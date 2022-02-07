import open3d as o3d


def fpfh(pcd, voxel_size):
    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_fpfh


def ransac_based_on_fpfh(source, target, voxel_size, fast):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    print("   option fast %d" % fast)

    if not fast:
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
    else:
        result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
            source, target, fpfh(source, voxel_size), fpfh(target, voxel_size),
            o3d.pipelines.registration.FastGlobalRegistrationOption(
                maximum_correspondence_distance=distance_threshold))
    return result