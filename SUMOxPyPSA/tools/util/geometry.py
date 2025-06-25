from __future__ import print_function, division
import collections


def cross_vertical(line_d, line_v):
    pt_d1, pt_d2 = line_d
    pt_v1, pt_v2 = line_v
    x_d1, y_d1 = pt_d1
    x_d2, y_d2 = pt_d2

    dy_d = y_d2 - y_d1
    dx_d = x_d2 - x_d1
    if dx_d == 0:
        # parallel (vertical) line
        return None
    slope_d = dy_d / dx_d
    intercept_d = y_d1 - slope_d * x_d1

    x_v, y_v1     = pt_v1
    x_v, y_v2     = pt_v2
    if x_v < min(x_d1, x_d2) or x_v > max(x_d1, x_d2):
        return None

    y_meet = slope_d * x_v + intercept_d
    if min(y_v1, y_v2) <= y_meet <= max(y_v1, y_v2):
        return x_v, y_meet
    return None

def cross_line(line_a, line_b):
    pt_a1, pt_a2 = line_a
    pt_b1, pt_b2 = line_b
    x_a1, y_a1 = pt_a1
    x_a2, y_a2 = pt_a2
    x_b1, y_b1 = pt_b1
    x_b2, y_b2 = pt_b2

    dy_a = y_a2 - y_a1
    dx_a = x_a2 - x_a1
    dy_b = y_b2 - y_b1
    dx_b = x_b2 - x_b1

    if dx_a == 0:
        return cross_vertical(line_b, line_a)
    if dx_b == 0:
        return cross_vertical(line_a, line_b)

    slope_a = dy_a / dx_a
    slope_b = dy_b / dx_b
    intercept_a = y_a1 - slope_a * x_a1
    intercept_b = y_b1 - slope_b * x_b1
    if slope_a == slope_b:
        # parallel lines, never meet
        return None
    x_meet = (intercept_b - intercept_a) / (slope_a - slope_b)
    y_meet = slope_a * x_meet + intercept_a
    if max(min(x_a1, x_a2), min(x_b1, x_b2)) <= x_meet <= min(max(x_a1, x_a2), max(x_b1, x_b2)):
        return x_meet, y_meet
    return None

def edges(polygon):
    for i in range(1, len(polygon)):
        yield polygon[i-1], polygon[i]
    if polygon[0] != polygon[-1]:
        yield polygon[-1], polygon[0]



def polygon_includes(polygon, point):
    x, y = zip(*polygon)
    line_left   = ((min(x), point[1]), (point[0], point[1]))
    line_right  = ((point[0], point[1]), (max(x), point[1]))
    # The set is necessary to eliminate duplicate points, which happens
    # when a node is crossed exactly, in which case the line crosses
    # two edges rather than one
    cross_left  = set(cross_line(line_left, edge)
                      for edge in edges(polygon)) - {None}
    cross_right = set(cross_line(line_right, edge)

                      for edge in edges(polygon)) - {None}
    return (len(cross_left) & 1) == 1 and (len(cross_right) & 1) == 1


class Edges(object):
    def __init__(self, points):
        self.points = points

    def __getitem__(self, idx):
        if 0 <= idx < len(self.points) - 1:
            return self.points[idx], self.points[idx+1]
        elif idx == len(self.points) - 1:
            return self.points[idx], self.points[0]
        elif -len(self.points) < idx < 0:
            return self[idx+len(self.points)]
        else:
            raise IndexError("%s not in %s" % (idx, len(self.points)))

    def __iter__(self):
        for i in range(len(self.points)):
            yield self[i]


class IntervalTree(object):
    Node = collections.namedtuple('Node', ['left','right','interval','value'])

    def __init__(self, intervals):
        # first, transform of a,b into min(a,b),max(a,b), i sorted
        prepared = sorted((min(x1,x2),max(x1,x2), i) for (i, (x1, x2)) in enumerate(intervals))
        # then recursively build a tree
        self.root = self._build_tree(prepared, 0, len(prepared))

    def _build_tree(self, sorted_intervals, left, right):
        if left == right or left + 1 == right:
            # leaf node
            return self.Node(None, None, sorted_intervals[left][0:2], sorted_intervals[left][2])
        else:
            mid        = (left + right) // 2
            left_node  = self._build_tree(sorted_intervals, left, mid)
            right_node = self._build_tree(sorted_intervals, mid, right)
            interval   = left_node.interval[0], max(left_node.interval[1], right_node.interval[1])
            # interior node
            return self.Node(left_node, right_node, interval, None)

    def _query_tree(self, node, x):
        min_x, max_x = node.interval
        results      = []
        if min_x > x or max_x < x:
            return results
        if node.left is not None:
            results.extend(self._query_tree(node.left, x))
        if node.right is not None:
            results.extend(self._query_tree(node.right, x))
        if node.value is not None:
            results.append(node.value)
        return results

    def __getitem__(self, x):
        return self._query_tree(self.root, x)


class Polygon(object):
    def __init__(self, points):
        self.points  = points
        self.edges   = Edges(points)
        # build vertical extent tree for efficient point-in-polygon query
        verticals = ((y1, y2) for ((x1,y1), (x2, y2)) in self.edges)
        self.vertical_intervals = IntervalTree(verticals)

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def __contains__(self, point):
        x, y        = point
        left, right = 0, 0
        # don't have min/max handy, so this will have to do
        horizontal  = ((-180, y), (180, y))
        # a horizontal line at y crosses the edges given by the idxs
        cross_pts = set()
        cross_left, cross_right = 0, 0
        # check if they cross an odd number of times on right and left sides
        for i in self.vertical_intervals[y]:
            cross_x, cross_y = cross_line(horizontal, self.edges[i])
            if cross_x in cross_pts:
                continue
            cross_pts.add(cross_x)
            if cross_x < x:
                cross_left += 1
            else:
                cross_right += 1
        if cross_left & 1 == 1 and cross_right & 1 == 1:
            return True
        return False

    def to_wkt(self):
        return 'POLYGON(({0}))'.format(','.join('{0} {1}'.format(x, y) for (x,y) in self.points))


if __name__ == '__main__':
    line_a = ((1,1), (3,4))
    line_b = ((1,3), (3,2))
    line_c = ((1,6), (3,5))
    line_v = ((2, 0), (2, 4))

    assert cross_line(line_a, line_b) == (2.0, 2.5)
    assert cross_line(reversed(line_a), line_b) == (2.0, 2.5)
    assert cross_line(line_v, line_b) == (2.0, 2.5)
    assert cross_line(line_b, line_c) is None

    square = ((0,0), (0,5),
               (5,5), (5,0))
    point = (2,2)
    assert polygon_includes(square, point)
    assert not polygon_includes(square, (7, 2))

    pentagon = ((1,0), (0, 2), (2, 3), (4,2), (3,0))
    assert polygon_includes(pentagon, (2, 2))
    assert not polygon_includes(pentagon, (1,3))
    print("done")
