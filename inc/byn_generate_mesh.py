import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh

edges = mp_face_mesh.FACEMESH_TESSELATION
edges = edges.union(mp_face_mesh.FACEMESH_CONTOURS)
edges = edges.union(mp_face_mesh.FACEMESH_IRISES)

list_of_verticies = set()
edge_mapping = dict()
for edge in edges:
    vert_1 = edge[0]
    vert_2 = edge[1]
    list_of_verticies.add(vert_1)
    list_of_verticies.add(vert_2)
    if(vert_1 not in edge_mapping):
        edge_mapping[vert_1] = list([vert_2])
    else:
        edge_mapping[vert_1].append(vert_2)

def short_order_tuple(tuple):
    if(tuple[0] < tuple[1]):
        return (tuple[0], tuple[1])
    else:
        return (tuple[1], tuple[0])

def is_short_loop(vert, pred):
    path = []
    crawl = vert
    path.append(crawl)
    count = 0
    while (True):
        path.append(pred[crawl])
        crawl = pred[crawl]
        if(crawl == vert):
            break
        count = count + 1
        if(count > 10):
            return False
    return len(path)==3

def BFS(adj, src, dest, v, pred, dist):
    # a queue to maintain queue of vertices whose
    # adjacency list is to be scanned as per normal
    # DFS algorithm
    queue = []
  
    # boolean array visited[] which stores the
    # information whether ith vertex is reached
    # at least once in the Breadth first search
    visited = [False for i in range(v)];
  
    # initially all vertices are unvisited
    # so v[i] for all i is false
    # and as no path is yet constructed
    # dist[i] for all i set to infinity
    for i in range(v):
 
        dist[i] = 1000000
        pred[i] = -1
     
    # now source is first to be visited and
    # distance from source to itself should be 0
    visited[src] = False
    dist[src] = 0
    queue.append(src)
    
    visted_edge = set()
    # standard BFS algorithm
    while (len(queue) != 0):
        u = queue[0]
        queue.pop(0)
        for i in range(len(adj[u])):
            if(adj[u][i] == dest and is_short_loop(src, pred)):
                continue

            if (visited[adj[u][i]] == False ):

                #visted_edge.add(edge_tuple)

                visited[adj[u][i]] = True
                dist[adj[u][i]] = dist[u] + 1
                pred[adj[u][i]] = u
                queue.append(adj[u][i])
  
                # We stop BFS when we find
                # destination.
                if (adj[u][i] == dest):
                    return True
  
    return False



# Python3 program to detect cycle in
# an undirected graph using BFS.
from collections import deque
 
def addEdge(adj: list, u, v):
    adj[u].append(v)
    adj[v].append(u)
 
def isCyclicConnected(adj: list, s, V,
                      visited: list):
 
    # Set parent vertex for every vertex as -1.
    parent = [-1] * V
 
    # Create a queue for BFS
    q = deque()
 
    # Mark the current node as
    # visited and enqueue it
    visited[s] = True
    q.append(s)
 
    while q != []:
 
        # Dequeue a vertex from queue and print it
        u = q.pop()
 
        # Get all adjacent vertices of the dequeued
        # vertex u. If a adjacent has not been visited,
        # then mark it visited and enqueue it. We also
        # mark parent so that parent is not considered
        # for cycle.
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                q.append(v)
                parent[v] = u
            elif parent[u] != v:


                return True
 
    return False
 
def isCyclicDisconnected(adj: list, V):
 
    # Mark all the vertices as not visited
    visited = [False] * V
 
    for i in range(V):
        if not visited[i] and \
               isCyclicConnected(adj, i, V, visited):
            return True
    return False

#def dfs(graph, start, end):
#    count = 0
#    fringe = [(start, [])]
#    while fringe:
#        state, path = fringe.pop()
#        if path and state == end:
#            yield path
#            count = count + 1
#            if(count >= len(graph[start])):
#                return
#            continue
#        for next_state in graph[state]:
#            if next_state in path:
#                continue
#            fringe.append((next_state, path+[next_state]))
#
#cycles = set()
#for node in list_of_verticies:
#    print(node)
#    for path in dfs(edge_mapping, node, node):
#        cycles.add(tuple([node]+path))
#    print(cycles)




#
#def find_loops(neighbor_mapping, start, end, current_path):
#    valid_paths = set()
#    for neighbor in neighbor_mapping[start]:
#        if(neighbor in current_path):
#            continue
#        if( neighbor == end ):
#            valid_paths.add(tuple(current_path))
#        else:
#            next_path = current_path + [neighbor]
#            new_loops = find_loops(neighbor_mapping, neighbor, end, next_path)
#            valid_paths = valid_paths.union(new_loops)
#    return valid_paths
#    
all_loops = set()
for vert in list_of_verticies:
    print(vert)
    v = len(list_of_verticies)
    pred=[0 for i in range(v)]
    dist=[0 for i in range(v)]
    #try:
    if(True):
        if(not BFS(edge_mapping, vert, vert, v, pred, dist)):
            print("contiuing")
            continue
        break     
        path = []
        crawl = vert
        path.append(crawl)
         
        while (True):
            path.append(pred[crawl])
            crawl = pred[crawl]
            if(crawl == vert):
                break
        
            

        print(path)
    #except:
    #    print("failed")

print(all_loops)