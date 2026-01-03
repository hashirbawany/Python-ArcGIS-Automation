#Section 1 : Setting things up

#1.1: initializing API
import arcpy

#1.2: loading project & file paths
aprx = arcpy.mp.ArcGISProject(r"C:\Users\Public\ArcGis project\ArcGis project.aprx")

arcpy.env.overwriteOutput = True 
original_data_path = r"C:\Users\hashi\OneDrive - Higher Education Commission\Desktop\Uchicago Classes\Quarter 4\GIS\Final Project\Final\Shapefiles\harris_underinsurance.shp"
copy_data_path = r"C:\Users\Public\ArcGis project\harris_underinsurance_edit.shp"

arcpy.management.CopyFeatures(original_data_path, copy_data_path)

#1.3: deleting all previous maps
for m in aprx.listMaps():
    aprx.deleteItem(m)

#1.4: Defining function to create map objects
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

#1.5: Defining function to create layouts
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



#Section 2: Creating maps

#2.1: creating map for locating risk zones

risk_map = {
    0: "No Rating",
    1: "Very Low",
    2: "Relatively Low",
    3: "Relatively Moderate",
    4: "Relatively High",
    5: "Very High"
}

m,layer = create_single_map(
    "risk_map",
    copy_data_path,
    "harris_underinsurance",
    "UniqueValueRenderer",
    "RFLD_RIS_1" ,
    "Yellow-Green-Blue (6 Classes)",
    risk_map )



#2.2: Creating map for insurance gaps
insurance_map = {
    -1: "No Gap",
    0: "Low Gap",
    1: "Medium Gap",
    2: "High Gap"
}


n,layer2 = create_single_map(
    "insurance_map",
    copy_data_path,
    "harris_underinsurance",
    "UniqueValueRenderer",
    "jenks_clas" ,
    "Yellow-Green-Blue (4 Classes)",
    insurance_map )



#Section 3: Creating Layouts

#3.1 removing all layouts
for layout in aprx.listLayouts():
    aprx.deleteItem(layout)



#3.2: Creating layout for risk
risk_layout  = create_standard_layout(
    m,
    layer,
    "risk_map",
    "Figure 1: Flood Risk Index in Harris County, Texas")



#3.3: Creating layout for insurance gap
insurance_layout = create_standard_layout(
    n,
    layer2,
    "insurance_layout",
    "Figure 2: Insurance Gap in Harris County, Texas" )



#Section 4: Saving & Exporting
#4.1: Saving Project
aprx.save()

#4.2: Exporting layout as png
output_lyt1 = r"C:\Users\Public\ArcGis project\layout_1.png"
output_lyt2 = r"C:\Users\Public\ArcGis project\layout_2.png"

risk_layout.exportToPNG(
    output_lyt1,
    resolution=300
)

insurance_layout.exportToPNG(
    output_lyt2,
    resolution=300
)


