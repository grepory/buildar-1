import boto3

from buildar.pipeline.step import Step

class Tagger(Step):
    def build(self, build_context):
        self._ec2 = boto3.client('ec2', region_name=build_context['build_region'])
        regions = self._ec2.describe_regions()['Regions']

        for r in regions:
            region_name = r['RegionName']
            region_client = boto3.client('ec2', region_name=region_name)

            resp = region_client.describe_images(
                    Filters=[
                        {
                            'Name': 'name',
                            'Values': [build_context['image_name']],
                        },
                    ])

            image = resp['Images'][0]
            release = [x for x in image['Tags'] if x['Key'] == 'release'][0]['Value']
            sha = [x for x in image['Tags'] if x['Key'] == 'sha'][0]['Value']

            region_client.create_tags(Resources=[image['ImageId']],
                    Tags=[
                        {
                            'Key': 'release',
                            'Value': build_context.get('release_tag', release),
                        },
                        {
                            'Key': 'sha',
                            'Value': build_context.get('bastion_version', sha),
                        },
                        {
                            'Key': 'opsee',
                            'Value': 'bastion',
                        },
                    ])

        build_context
    
    def cleanup(self, build_context):
        build_context