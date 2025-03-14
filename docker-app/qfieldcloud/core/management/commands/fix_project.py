from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import io
import logging
import os
from qfieldcloud.core.models import Project

class Command(BaseCommand):
    help = 'Fix project by creating a valid QGIS project file'

    def add_arguments(self, parser):
        parser.add_argument('project_name', type=str, help='Name of the project to fix')

    def handle(self, *args, **options):
        project_name = options['project_name']
        
        try:
            # Get the project
            project = Project.objects.get(name=project_name)
            self.stdout.write(f'Found project: {project.name} (ID: {project.id})')
            self.stdout.write(f'Current status: {project.status}')
            
            # Get storage configuration
            storage_config = settings.STORAGES['default']
            
            # Create S3 client
            s3 = boto3.resource(
                's3',
                endpoint_url=storage_config['OPTIONS']['endpoint_url'],
                aws_access_key_id=storage_config['OPTIONS']['access_key'],
                aws_secret_access_key=storage_config['OPTIONS']['secret_key'],
                region_name=storage_config['OPTIONS'].get('region_name', 'us-east-1')
            )
            
            # Get the bucket
            bucket_name = storage_config['OPTIONS']['bucket_name']
            bucket = s3.Bucket(bucket_name)
            
            # Check if the project directory exists
            project_prefix = f'projects/{project.id}/'
            objects = list(bucket.objects.filter(Prefix=project_prefix))
            
            self.stdout.write(f'Found {len(objects)} objects in project directory')
            for obj in objects:
                self.stdout.write(f'- {obj.key}')
            
            # Check if a QGIS project file already exists
            qgis_files = [obj for obj in objects if obj.key.endswith('.qgs') or obj.key.endswith('.qgz')]
            
            if qgis_files:
                self.stdout.write(self.style.SUCCESS(f'QGIS project file already exists: {qgis_files[0].key}'))
                return
            
            # Create a basic QGIS project file
            qgis_project_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="teste" version="3.22.0-Białowieża">
  <title>teste</title>
  <autotransaction active="0"/>
  <evaluateDefaultValues active="0"/>
  <trust active="0"/>
  <projectCrs>
    <spatialrefsys>
      <wkt>GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["unknown"],AREA["World"],BBOX[-90,-180,90,180]],ID["EPSG",4326]]</wkt>
      <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
      <srsid>3452</srsid>
      <srid>4326</srid>
      <authid>EPSG:4326</authid>
      <description>WGS 84</description>
      <projectionacronym>longlat</projectionacronym>
      <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
      <geographicflag>true</geographicflag>
    </spatialrefsys>
  </projectCrs>
  <layer-tree-group>
    <customproperties/>
    <custom-order enabled="0"/>
  </layer-tree-group>
  <snapping-settings enabled="0" mode="2" tolerance="12" unit="1" intersection-snapping="0" type="1">
    <individual-layer-settings/>
  </snapping-settings>
  <relations/>
  <mapcanvas name="theMapCanvas" annotationsVisible="1">
    <units>degrees</units>
    <extent>
      <xmin>-180</xmin>
      <ymin>-90</ymin>
      <xmax>180</xmax>
      <ymax>90</ymax>
    </extent>
    <rotation>0</rotation>
    <destinationsrs>
      <spatialrefsys>
        <wkt>GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["unknown"],AREA["World"],BBOX[-90,-180,90,180]],ID["EPSG",4326]]</wkt>
        <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
        <srsid>3452</srsid>
        <srid>4326</srid>
        <authid>EPSG:4326</authid>
        <description>WGS 84</description>
        <projectionacronym>longlat</projectionacronym>
        <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
        <geographicflag>true</geographicflag>
      </spatialrefsys>
    </destinationsrs>
    <rendermaptile>0</rendermaptile>
    <expressionContextScope/>
  </mapcanvas>
  <projectModels/>
  <legend updateDrawingOrder="true"/>
  <mapViewDocks/>
  <mapViewDocks3D/>
  <main-annotation-layer autoRefreshEnabled="0" refreshOnNotifyEnabled="0" autoRefreshTime="0" type="annotation" refreshOnNotifyMessage="">
    <id>Annotations_c7f2f0f0_6e38_4b8d_b0d4_b0f9f8f8f8f8</id>
    <datasource></datasource>
    <keywordList>
      <value></value>
    </keywordList>
    <layername>Annotations</layername>
    <srs>
      <spatialrefsys>
        <wkt>GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["unknown"],AREA["World"],BBOX[-90,-180,90,180]],ID["EPSG",4326]]</wkt>
        <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
        <srsid>3452</srsid>
        <srid>4326</srid>
        <authid>EPSG:4326</authid>
        <description>WGS 84</description>
        <projectionacronym>longlat</projectionacronym>
        <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
        <geographicflag>true</geographicflag>
      </spatialrefsys>
    </srs>
    <resourceMetadata>
      <identifier></identifier>
      <parentidentifier></parentidentifier>
      <language></language>
      <type></type>
      <title></title>
      <abstract></abstract>
      <links/>
      <fees></fees>
      <encoding></encoding>
      <crs>
        <spatialrefsys>
          <wkt></wkt>
          <proj4></proj4>
          <srsid>0</srsid>
          <srid>0</srid>
          <authid></authid>
          <description></description>
          <projectionacronym></projectionacronym>
          <ellipsoidacronym></ellipsoidacronym>
          <geographicflag>false</geographicflag>
        </spatialrefsys>
      </crs>
      <extent/>
    </resourceMetadata>
    <items/>
    <layerOpacity>1</layerOpacity>
  </main-annotation-layer>
  <projectlayers/>
  <layerorder/>
  <properties>
    <Digitizing>
      <AvoidIntersectionsMode type="int">0</AvoidIntersectionsMode>
    </Digitizing>
    <Gui>
      <CanvasColorBluePart type="int">255</CanvasColorBluePart>
      <CanvasColorGreenPart type="int">255</CanvasColorGreenPart>
      <CanvasColorRedPart type="int">255</CanvasColorRedPart>
      <SelectionColorAlphaPart type="int">255</SelectionColorAlphaPart>
      <SelectionColorBluePart type="int">0</SelectionColorBluePart>
      <SelectionColorGreenPart type="int">255</SelectionColorGreenPart>
      <SelectionColorRedPart type="int">255</SelectionColorRedPart>
    </Gui>
    <Legend>
      <filterByMap type="bool">false</filterByMap>
    </Legend>
    <Measure>
      <Ellipsoid type="QString">EPSG:7030</Ellipsoid>
    </Measure>
    <Measurement>
      <AreaUnits type="QString">m2</AreaUnits>
      <DistanceUnits type="QString">meters</DistanceUnits>
    </Measurement>
    <PAL>
      <CandidatesLinePerCM type="double">5</CandidatesLinePerCM>
      <CandidatesPolygonPerCM type="double">2.5</CandidatesPolygonPerCM>
      <DrawRectOnly type="bool">false</DrawRectOnly>
      <DrawUnplaced type="bool">false</DrawUnplaced>
      <PlacementEngineVersion type="int">1</PlacementEngineVersion>
      <SearchMethod type="int">0</SearchMethod>
      <ShowingAllLabels type="bool">false</ShowingAllLabels>
      <ShowingCandidates type="bool">false</ShowingCandidates>
      <ShowingPartialsLabels type="bool">true</ShowingPartialsLabels>
      <TextFormat type="int">0</TextFormat>
      <UnplacedColor type="QString">255,0,0,255</UnplacedColor>
    </PAL>
    <Paths>
      <Absolute type="bool">false</Absolute>
    </Paths>
    <PositionPrecision>
      <Automatic type="bool">true</Automatic>
      <DecimalPlaces type="int">2</DecimalPlaces>
    </PositionPrecision>
    <SpatialRefSys>
      <ProjectionsEnabled type="int">1</ProjectionsEnabled>
    </SpatialRefSys>
  </properties>
  <dataDefinedServerProperties>
    <Option type="Map">
      <Option name="name" type="QString" value=""/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </dataDefinedServerProperties>
  <visibility-presets/>
  <transformContext/>
  <projectMetadata>
    <identifier></identifier>
    <parentidentifier></parentidentifier>
    <language></language>
    <type></type>
    <title></title>
    <abstract></abstract>
    <links/>
    <author>QFieldCloud</author>
    <creation>2025-03-11T18:00:00</creation>
  </projectMetadata>
  <Annotations/>
  <Layouts/>
  <Bookmarks/>
  <ProjectViewSettings UseProjectScales="0">
    <Scales/>
    <DefaultViewExtent xmax="1" xmin="-1" ymax="1" ymin="-1">
      <spatialrefsys>
        <wkt>GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["unknown"],AREA["World"],BBOX[-90,-180,90,180]],ID["EPSG",4326]]</wkt>
        <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
        <srsid>3452</srsid>
        <srid>4326</srid>
        <authid>EPSG:4326</authid>
        <description>WGS 84</description>
        <projectionacronym>longlat</projectionacronym>
        <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
        <geographicflag>true</geographicflag>
      </spatialrefsys>
    </DefaultViewExtent>
  </ProjectViewSettings>
</qgis>
"""
            
            # Upload the QGIS project file
            qgis_project_key = f'projects/{project.id}/teste.qgs'
            bucket.put_object(
                Key=qgis_project_key,
                Body=qgis_project_content.encode('utf-8'),
                ContentType='application/xml'
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created QGIS project file: {qgis_project_key}'))
            
            # Trigger project processing
            project.process()
            
            self.stdout.write(self.style.SUCCESS(f'Triggered project processing'))
            self.stdout.write(f'New status: {project.status}')
            
            # Provide instructions
            self.stdout.write('\nInstructions:')
            self.stdout.write('1. Wait a few moments for the project to be processed')
            self.stdout.write('2. Check the project status again with:')
            self.stdout.write('   docker-compose exec app python manage.py shell -c "from qfieldcloud.core.models import Project; p = Project.objects.get(name=\'teste\'); print(\'Status:\', p.status)"')
            self.stdout.write('3. If the status is still "failed", try restarting the worker:')
            self.stdout.write('   docker-compose restart worker')
            
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project not found: {project_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
