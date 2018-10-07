#!/usr/local/bin/python3
import boto3
import sys

def append_instance_info_to_each_lists(reservation):
    for instance in reservation['Instances']:
        all_instance_ids.append(instance['InstanceId'])
        append_name_and_status_to_list(instance)

def append_name_and_status_to_list(instance):
    instance_state = instance['State']['Name']
    instance_id = instance['InstanceId']
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            name_tag = tag['Value']
            instance_names_and_status.append(name_tag + "(" + instance_id + ")：" + instance_state)
            continue

def check_ec2_ip(instances):
    answer = input()
    if answer != 'y':
      return
    
    for instance in instances:   
        instance.wait_until_running()
        print("インスタンスID[" + instance.instance_id + "]のGIP：" + instance.public_ip_address)

client = boto3.client('ec2')

instance_names_and_status = []
all_instance_ids = []

res = client.describe_instances()
for reservation in res['Reservations']:
    append_instance_info_to_each_lists(reservation)

for (num, detail) in enumerate(instance_names_and_status):
    print("[" +  str(num) + "]" + detail)

print('')
print('続けて')
print('インスタンスの起動をおこなう場合は 1 ')
print('インスタンスの停止をおこなう場合は 2 ')
print('起動と停止を両方おこないたい場合は 3 ')
print('終了する場合はそれ以外のてきとーな値をそれぞれ入力してください')
option = int(input())

if not option in [1 ,2 ,3]:
    print('ばいばいっ！')
    sys.exit()

ec2 = boto3.resource('ec2')
if option in [1, 3]:
    print('起動したいEC2の番号を入力してください')
    print('複数対象がある場合は半角スペースで区切って入力してください')
    raunch_instance_ids = map(int, input().split())
    instances = []

    for id in raunch_instance_ids:
        instance = ec2.Instance(all_instance_ids[id])
        instances.append(instance)
        instance.start()
    print('起動処理おわったよ')
    print('続けて、起動したインスタンスのGIPを確認しますか？（y/n）')
    check_ec2_ip(instances)


if option in [2, 3]:
    print('停止したいEC2の番号を入力してください')
    print('複数対象がある場合は半角スペースで区切って入力してください')
    stop_instance_ids = map(int, input().split())

    for id in stop_instance_ids:
        instance = ec2.Instance(all_instance_ids[id])
        instance.stop()
    print('停止処理おわったよ')

print('ばいばいっ！')
