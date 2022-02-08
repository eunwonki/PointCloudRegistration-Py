import open3d as o3d
import numpy as np
import time
from panda3d.core import *

import localregistration
import globalregistration


def array_to_mat4(a):
    return LMatrix4f(
        a[0], a[4], a[8], a[12],
        a[1], a[5], a[9], a[13],
        a[2], a[6], a[10], a[14],
        a[3], a[7], a[11], a[15],
    )


def numpy_array_to_mat4(a):
    return LMatrix4f(
        a[0][0], a[1][0], a[2][0], a[3][0],
        a[0][1], a[1][1], a[2][1], a[3][1],
        a[0][2], a[1][2], a[2][2], a[3][2],
        a[0][3], a[1][3], a[2][3], a[3][3],
    )


def mat4_to_numpy_array(a):
    return np.array(
        [a[0], a[1], a[2], a[3]],
        [a[4], a[5], a[6], a[7]],
        [a[8], a[9], a[10], a[11]],
        [a[12], a[13], a[14], a[15]]
    )


def process(source_node, voxel_size):
    pcd = geom_node_to_pcd(source_node)
    downsampled_pcd = down_sampling(pcd, voxel_size)
    return pcd_to_geom_node(downsampled_pcd)


def global_registration(source_node, target_node, voxel_size, fast):
    source_pcd = geom_node_to_pcd(source_node)
    target_pcd = geom_node_to_pcd(target_node)
    start = time.time()
    result = globalregistration.ransac_based_on_fpfh(source_pcd, target_pcd, voxel_size, fast)
    print("Cost Time: %.3f sec" % (time.time() - start))
    return result


def local_registration(source_node, target_node, initial_transformation, voxel_size):
    start = time.time()
    #pose = localregistration.opencv_icp(source_node, target_node, initial_transformation)
    #pose = localregistration.open3d_icp(source_node, target_node, initial_transformation, voxel_size)
    pose = localregistration.open3d_gicp(source_node, target_node, initial_transformation, voxel_size)
    print("Cost Time: %.3f sec" % (time.time() - start))
    return pose


def mesh_node_to_point_cloud_node(source_node):
    numOfVertex = source_node.node().getGeom(0).getVertexData().getNumRows()

    _format = GeomVertexFormat.getV3n3c4()
    vertex_data = GeomVertexData('pc', _format, Geom.UH_static)
    vertex = GeomVertexWriter(vertex_data, 'vertex')
    s_vertex = GeomVertexReader(source_node.node().getGeom(0).getVertexData(), 'vertex')
    while not s_vertex.isAtEnd():
        vertex.addData3(s_vertex.getData3())
    normal = GeomVertexWriter(vertex_data, 'normal')
    s_normal = GeomVertexReader(source_node.node().getGeom(0).getVertexData(), 'normal')
    while not s_normal.isAtEnd():
        normal.addData3(s_normal.getData3())
    color = GeomVertexWriter(vertex_data, 'color')
    s_color = GeomVertexReader(source_node.node().getGeom(0).getVertexData(), 'color')
    while not s_color.isAtEnd():
        color.addData3(s_color.getData3())

    prim = GeomPoints(Geom.UH_static)
    prim.add_next_vertices(numOfVertex)

    geom = Geom(vertex_data)
    geom.addPrimitive(prim)
    node = GeomNode('PointCloud')
    node.addGeom(geom)

    node = NodePath(node)
    return node


def geom_node_to_pcd(geom_node):
    pcd = o3d.geometry.PointCloud()

    _format = GeomVertexFormat.getV3t2()
    s_vertex = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'vertex')
    while not s_vertex.isAtEnd():
        vertex = s_vertex.getData3()
        pcd.points.append(vertex)

    s_normal = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'normal')
    while not s_normal.isAtEnd():
        normal = s_normal.getData3()
        pcd.normals.append(normal)

    s_color = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'color')
    while not s_color.isAtEnd():
        color = s_color.getData3()
        pcd.colors.append(color)

    return pcd


def pcd_to_geom_node(pcd):
    num_of_vertex = len(pcd.points)

    _format = GeomVertexFormat.getV3n3c4()
    vertex_data = GeomVertexData('pc', _format, Geom.UHDynamic)
    vertex_data.setNumRows(2)

    vertex = GeomVertexWriter(vertex_data, 'vertex')
    normal = GeomVertexWriter(vertex_data, 'normal')
    color = GeomVertexWriter(vertex_data, 'color')

    for point in pcd.points:
        vertex.addData3(point[0], point[1], point[2])
    for point_normal in pcd.normals:
        normal.addData3(point_normal[0], point_normal[1], point_normal[2])
    for point_color in pcd.colors:
        color.addData3(point_color[0], point_color[1], point_color[2])

    prim = GeomPoints(Geom.UH_static)
    prim.add_next_vertices(num_of_vertex)
    geom = Geom(vertex_data)
    geom.addPrimitive(prim)

    node = GeomNode('PointCloud')
    node.addGeom(geom)
    node = NodePath(node)
    return node


def geom_node_to_numpy_pc(geom_node):
    array = [[], []]
    vertices = []

    _format = GeomVertexFormat.getV3t2()
    s_vertex = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'vertex')
    while not s_vertex.isAtEnd():
        vertex = s_vertex.getData3()
        array[0].append(vertex)

    s_normal = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'normal')
    while not s_normal.isAtEnd():
        normal = s_normal.getData3()
        array[1].append(normal)

    component_count = 6
    has_normal = len(array[1]) > 0
    if has_normal:
        for i in range(len(array[1])):
            vertex = array[0][i]
            normal = array[1][i]
            vertices.append([vertex[0], vertex[1], vertex[2], normal[0], normal[1], normal[2]])

    else:
        component_count = 3
        vertices = array[0]

    return np.array(vertices).reshape((-1, component_count)).astype(np.float32)


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