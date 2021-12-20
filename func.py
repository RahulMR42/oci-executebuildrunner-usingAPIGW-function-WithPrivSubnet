# oci-load-file-into-adw-python version 1.0.
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import io
import os
import json
import logging
from git import Repo

from fdk import response

class git_actions:
    def __init__(self):
        self.target_dir = '/tmp/source'

    def git_clone(self,bb_user,bb_url,bb_slug,bb_branch,oci_ocr_target_repo,bb_commit_message):
        try:
            Repo.clone_from(bb_url,self.target_dir)
            

        except Exception as error:
            logging.getLogger().error('Exception' + str (error)) 

def handler(ctx, data: io.BytesIO=None):
    try:
        body = json.loads(data.getvalue())
        bb_user = body['actor']['display_name'].replace(" ", "")
        bb_url = body['push']['changes'][0]['new']['links']['html']['href']
        bb_repo_name = bb_url.split("/")[-3]
        bb_branch = body['push']['changes'][0]['new']['name']
        bb_slug = body['repository']['workspace']['slug']
        bb_commit_message = body['push']['changes'][0]['new']['target']['summary']['raw'].replace("\n", "")
        oci_ocr_user = os.environ['oci_ocr_user']
        oci_region = os.environ['oci_region']
        oci_tenacy_namespace = os.environ['oci_tenacy_namespace']
        oci_ocr_project = os.environ['oci_ocr_project']
        oci_ocr_target_repo = f"https://devops.scmservice.${oci_region}.oci.oraclecloud.com/namespaces/{oci_tenacy_namespace}/projects/{oci_ocr_project}/repositories/{bb_repo_name}"
        
        logging.getLogger().info(f"User - {bb_user},Url - {bb_url},User - {bb_slug},Commit - {bb_commit_message},Oracle User - {oci_ocr_user},Target Repo - {oci_ocr_target_repo}")
        git_object = git_actions()
        git_object.git_clone(bb_user,bb_url,bb_slug,bb_branch,oci_ocr_target_repo,bb_commit_message)

        logging.getLogger().info("Invoked function with default  image")
        return response.Response(
            ctx, 
            response_data=json.dumps({"status": "Hello World! with DefaultImage"}),
            headers={"Content-Type": "application/json"})
    except Exception as error:
        logging.getLogger().error("Exception" + str(error))
    