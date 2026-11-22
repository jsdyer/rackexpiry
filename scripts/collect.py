"""Snapshot a bounded, reviewed software catalogue. No user inventory is collected."""
import json,time
from common import getjson,save
PRODUCTS=['almalinux','ubuntu','debian','linuxmint','rocky-linux','php','nodejs','python','mariadb','mysql','postgresql','nginx','apache-http-server','redis','kubernetes','docker-engine','laravel','django','windows','windows-server','proxmox-ve','openssl','dotnet','fedora','centos-stream']
def normalize(raw,slug):
    result=raw.get('result',{})
    if result.get('name')!=slug or not result.get('releases'):raise ValueError('Unexpected product data')
    for release in result['releases']:
        if not isinstance(release.get('name'),str):raise ValueError('Missing release identity')
    return {'id':slug,'name':result['label'],'labels':result.get('labels',{}),'links':result.get('links',{}),'releases':result['releases'],'source_modified_at':raw.get('last_modified')}
def main():
    records=[];sources=[]
    for slug in PRODUCTS:
        url=f'https://endoflife.date/api/v1/products/{slug}/'
        print('Checking '+slug,flush=True)
        raw=getjson(url);records.append(normalize(raw,slug));sources.append({'name':'endoflife.date · '+slug,'url':url,'modified_at':raw.get('last_modified')});time.sleep(.3)
    save(records,sources=sources,coverage=f'{len(records)} selected software products; upstream community-maintained support windows. Vendor distribution backports and purchased extended support require separate verification.',warnings=['End-of-life means the selected upstream support window ended; it is not proof a machine is exploitable.','Extended support may require a paid contract. This tool does not assume you have one.'])
if __name__=='__main__':main()
