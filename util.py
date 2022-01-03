import open3d as o3d
import numpy as np
import time
from panda3d.core import *

import o3dmodule


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
    downsampled_pcd = o3dmodule.down_sampling(pcd, voxel_size)
    return pcd_to_geom_node(downsampled_pcd)


def global_registration(source_node, target_node, voxel_size, fast):
    source_pcd = geom_node_to_pcd(source_node)
    target_pcd = geom_node_to_pcd(target_node)
    start = time.time()
    result = o3dmodule.global_registration_ransac_based_on_fpfh(source_pcd, target_pcd, voxel_size, fast)
    print("Cost Time: %.3f sec" % (time.time() - start))
    return result


def local_registration(source_node, target_node, initial_transformation, voxel_size):
    source_pcd = geom_node_to_pcd(source_node)
    target_pcd = geom_node_to_pcd(target_node)
    start = time.time()
    result = o3dmodule.local_registration_gicp(source_pcd, target_pcd, initial_transformation, voxel_size)
    print("Cost Time: %.3f sec" % (time.time() - start))
    return result


def mesh_node_to_point_cloud_node(source_node):
    numOfVertex = source_node.node().getGeom(0).getVertexData().getNumRows()

    _format = GeomVertexFormat.getV3t2()
    vertex_data = GeomVertexData('pc', _format, Geom.UH_static)
    vertex = GeomVertexWriter(vertex_data, 'vertex')
    s_vertex = GeomVertexReader(source_node.node().getGeom(0).getVertexData(), 'vertex')
    while not s_vertex.isAtEnd():
        vertex.addData3(s_vertex.getData3())

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

    numOfVertex = geom_node.node().getGeom(0).getVertexData().getNumRows()

    _format = GeomVertexFormat.getV3t2()
    s_vertex = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'vertex')
    while not s_vertex.isAtEnd():
        vertex = s_vertex.getData3()
        pcd.points.append(vertex)

    s_normal = GeomVertexReader(geom_node.node().getGeom(0).getVertexData(), 'normal')
    while not s_normal.isAtEnd():
        vertex = s_normal.getData3()
        pcd.normals.append(vertex)

    return pcd


def pcd_to_geom_node(pcd):
    num_of_vertex = len(pcd.points)

    _format = GeomVertexFormat.getV3n3c4()
    vertex_data = GeomVertexData('pc', _format, Geom.UHDynamic)
    vertex_data.setNumRows(2)

    vertex = GeomVertexWriter(vertex_data, 'vertex')
    normal = GeomVertexWriter(vertex_data, 'normal')

    for point in pcd.points:
        vertex.addData3(point[0], point[1], point[2])
    for point_normal in pcd.normals:
        normal.addData3(point_normal[0], point_normal[1], point_normal[2])

    prim = GeomPoints(Geom.UH_static)
    prim.add_next_vertices(num_of_vertex)
    geom = Geom(vertex_data)
    geom.addPrimitive(prim)

    node = GeomNode('PointCloud')
    node.addGeom(geom)
    node = NodePath(node)
    return node