from qgis.core import (
    QgsProject,
    QgsFeatureRequest,
    QgsExpression,
    QgsVectorLayer,
    QgsFeature,
    QgsVectorFileWriter
)
from PyQt5.QtWidgets import QInputDialog, QFileDialog

# Get list of layer names
layers = QgsProject.instance().mapLayers().values()
layer_names = [layer.name() for layer in layers]

# Ask user to select a layer
selected_layer_name, ok = QInputDialog.getItem(
    None, 
    'Select Point Layer', 
    'Choose a point layer:', 
    layer_names, 
    0, 
    False
)

# Proceed if the user clicked OK
if ok:
    # Get the selected layer
    point_layer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]

    # Replace 'County' with the name of your column containing county information
    county_field_index = point_layer.fields().indexFromName('County')

    # Get unique county names
    unique_counties = point_layer.uniqueValues(county_field_index)

    # Ask user to select a directory to save the files
    save_directory = QFileDialog.getExistingDirectory(None, 'Select Directory to Save Layers')

    if save_directory:
        # Iterate over each unique county
        for county in unique_counties:
            # Create a filter expression to select features for the current county
            expression = QgsExpression(f'"County"=\'{county}\'')
            request = QgsFeatureRequest(expression)
            selected_features = [f for f in point_layer.getFeatures(request)]
            
            # Create a new memory layer for the current county
            crs = point_layer.crs()
            county_layer = QgsVectorLayer(f"Point?crs={crs.toWkt()}", f"{county} County", "memory")
            provider = county_layer.dataProvider()
            
            # Add fields to the new layer
            fields = point_layer.fields()
            provider.addAttributes(fields)
            county_layer.updateFields()
            
            # Add features to the new layer
            for feature in selected_features:
                new_feature = QgsFeature()
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes(feature.attributes())
                provider.addFeature(new_feature)
            
            # Add the new layer to the map
            QgsProject.instance().addMapLayer(county_layer)
            
            # Save the new layer to a file
            save_path = f"{save_directory}/{county}_County.shp"
            QgsVectorFileWriter.writeAsVectorFormat(
                county_layer,
                save_path,
                "UTF-8",
                crs,
                "ESRI Shapefile"
            )
