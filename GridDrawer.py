# %%
def compute_line_segment_through_image(center, direction_unit, width, height):
    """
    Compute the segment where a line through `center` in `direction_unit` intersects the image edges.
    Returns (start, end) tuple of points or None.
    """
    x0, y0 = center
    dx, dy = direction_unit
    points = []

    # Intersect with left (x = 0) and right (x = width - 1)
    for x_edge in [0, width - 1]:
        if dx != 0:
            t = (x_edge - x0) / dx
            y = y0 + t * dy
            if 0 <= y <= height - 1:
                points.append(np.array([x_edge, y]))

    # Intersect with top (y = 0) and bottom (y = height - 1)
    for y_edge in [0, height - 1]:
        if dy != 0:
            t = (y_edge - y0) / dy
            x = x0 + t * dx
            if 0 <= x <= width - 1:
                points.append(np.array([x, y_edge]))

    # Return first two valid edge-crossing points
    if len(points) >= 2:
        return points[0], points[1]
    return None

def extrapolate_parallel_lines_to_image(start1, end1, start2, image_shape):
    """
    Generate parallel lines from (start1 → end1) using spacing from start2,
    clipped exactly to the image edges.
    """
    height, width = image_shape
    direction = end1 - start1
    direction_unit = direction / np.linalg.norm(direction)
    normal = np.array([-direction_unit[1], direction_unit[0]])

    # Spacing between lines
    spacing = np.dot(start2 - start1, normal)
    # Ensure spacing is positive
    if spacing < 0:
        spacing *= -1
        normal *= -1
    # Determine how far we need to go based on projection of image corners
    corners = np.array([[0, 0], [0, height - 1], [width - 1, 0], [width - 1, height - 1]])
    offsets = np.dot(corners - start1, normal)
    min_offset, max_offset = np.min(offsets), np.max(offsets)

    # Number of lines
    n_neg = int(np.floor(min_offset / spacing))
    n_pos = int(np.ceil(max_offset / spacing))

    lines = []
    for i in range(n_neg, n_pos + 1):
        offset = i * spacing * normal
        center = start1 + offset
        clipped = compute_line_segment_through_image(center, direction_unit, width, height)
        if clipped is not None:
            lines.append(clipped)

    return lines

def plot_grid_over_image(image, hgrid, vgrid, h_color='cyan', v_color='magenta'):
    """
    Plot horizontal and vertical grid lines clipped to the image extent.
    """
    height, width = image.shape
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image, cmap='gray', origin='upper')

    for s, e in hgrid:
        ax.plot([s[0], e[0]], [s[1], e[1]], color=h_color, linewidth=0.5)

    for s, e in vgrid:
        ax.plot([s[0], e[0]], [s[1], e[1]], color=v_color, linewidth=0.5)

    ax.set_xlim(0, width - 1)
    ax.set_ylim(height - 1, 0)
    ax.set_title("Grid Overlay")
    plt.show()

hgrid = extrapolate_parallel_lines_to_image(
    np.array(hlines[0][0]), 
    np.array(hlines[0][1]), 
    np.array(hlines[1][0]), 
    frame.shape
)

vgrid = extrapolate_parallel_lines_to_image(
    np.array(vlines[0][0]), 
    np.array(vlines[0][1]), 
    np.array(vlines[1][0]), 
    frame.shape
)
print(vgrid, hgrid)
plot_grid_over_image(frame, hgrid, vgrid)
