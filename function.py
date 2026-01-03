import arcpy

# Defining function to create map objects
def create_single_map(
    map_name,
    layer_path,
    layer_name,
    renderer,
    variable_name,
    color_map,
    label_map=None,
    classification_method="NaturalBreaks",
    break_count=5
):
    m = aprx.createMap(map_name)
    layer = m.addDataFromPath(layer_path)
    layer.name = layer_name

    # remove basemap
    for lyr in m.listLayers():
        if lyr.isBasemapLayer:
            m.removeLayer(lyr)

    sym = layer.symbology
    sym.updateRenderer(renderer)

    ramp = aprx.listColorRamps(color_map)[0]
    sym.renderer.colorRamp = ramp

    # Categorical Value Renderer
    if renderer == "UniqueValueRenderer":
        sym.renderer.fields = [variable_name]

        items = sym.renderer.groups[0].items
        items.sort(key=lambda g: g.values[0][0])

        for item in items:
            val = int(item.values[0][0])
            item.label = label_map.get(val, str(val))

    # Continous Value Renderer
    elif renderer == "GraduatedColorsRenderer":
        sym.renderer.classificationField = variable_name
        sym.renderer.classificationMethod = classification_method 
        sym.renderer.breakCount = break_count
        sym.renderer.reclassify()

    else:
        raise ValueError(f"Unsupported renderer: {renderer}")

    layer.symbology = sym
    return m, layer



# Defining function to create layouts
def create_standard_layout(
    map_obj,
    layer,
    layout_name,
    title_text,
    mapframe_extent = None,
    title_position=(4.1215, 5.539),
    legend_position=(0.1464, 2.2927),
    legend_size=(1.2357, 1.7131),
    scalebar_position=(2.7713, 0.2371),
    north_arrow_position=(7.2704, 4.8844)
):

    # create layout
    layout = aprx.createLayout(8.27, 5.83, "INCH", layout_name)

    # create map frame
    if mapframe_extent is None:
        mapframe_extent = arcpy.Extent(
            0.885,
            0.665,
            7.385,
            5.165
        )
    mf = layout.createMapFrame(mapframe_extent, map_obj)

    # remove map frame border
    lyt_cim = layout.getDefinition("V3")
    for elm in lyt_cim.elements:
        if type(elm).__name__ == "CIMMapFrame":
            elm.graphicFrame.borderSymbol = None
    layout.setDefinition(lyt_cim)

    # zoom to layer
    mf.camera.setExtent(mf.getLayerExtent(layer))

    # title
    txt_style = aprx.listStyleItems(
        "ArcGIS 2D",
        "TEXT",
        "Title (Serif)")[0]

    title = aprx.createTextElement(
        layout,
        arcpy.Point(*title_position),
        "POINT",
        title_text,
        20,
        style_item=txt_style
    )

    title.setAnchor("Center_Point")
    title.elementPositionX = title_position[0]
    title.elementPositionY = title_position[1]
    title.fontFamilyName = "Garamond"

    # legend
    legend_style = aprx.listStyleItems(
        "ArcGIS 2D",
        "LEGEND",
        "Legend 1"
    )[0]

    legend = layout.createMapSurroundElement(
        arcpy.Point(*legend_position),
        "LEGEND",
        mf,
        legend_style
    )

    legend.elementWidth = legend_size[0]
    legend.elementHeight = legend_size[1]
    
    leg_cim = legend.getDefinition("V3")

    for item in leg_cim.items:
        # remove layer name
        item.showLayerName = False

        # remove field name
        item.showHeading = False

    legend.setDefinition(leg_cim)

    # scale bar
    scalebar_style = aprx.listStyleItems(
        "ArcGIS 2D",
        "SCALE_BAR",
        "Scale Line 1 Metric"
    )[0]

    layout.createMapSurroundElement(
        arcpy.Point(*scalebar_position),
        "SCALE_BAR",
        mf,
        scalebar_style
    )

    # north arrow
    north_arrow_style = aprx.listStyleItems(
        "ArcGIS 2D",
        "NORTH_ARROW",
        "ArcGIS North 1"
    )[0]

    layout.createMapSurroundElement(
        arcpy.Point(*north_arrow_position),
        "NORTH_ARROW",
        mf,
        north_arrow_style
    )

    return layout


