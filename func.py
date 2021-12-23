# oci-load-file-into-adw-python version 1.0.
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import io
import os
import oci
import uuid
import json
import base64
import logging
from git import Repo
import urllib.parse

from fdk import response


class secrets_action:
    def __init__(self,region):
        self.region = region 

    def read_secrets(self,oci_user_id,oci_ocr_password_id):
        try:
            logging.getLogger().info("Inside read secret function")
            signer = oci.auth.signers.get_resource_principals_signer()
            client = oci.secrets.SecretsClient({}, signer=signer)
            secret_content_ocr_user = client.get_secret_bundle(oci_user_id).data.secret_bundle_content.content.encode('utf-8')
            secret_content_ocr_user = base64.b64decode(secret_content_ocr_user).decode("utf-8")
            secret_content_ocr_password = client.get_secret_bundle(oci_ocr_password_id).data.secret_bundle_content.content.encode('utf-8')
            secret_content_ocr_password = base64.b64decode(secret_content_ocr_password).decode("utf-8")
            return secret_content_ocr_password,secret_content_ocr_user

        except Exception as error:
            logging.getLogger().error("Exception" + str(error))


class git_actions:
    def __init__(self):
        path_ref = uuid.uuid4().hex[:4]
        self.target_dir = f'/tmp/{path_ref}'

    def git_clone(self,bb_user,bb_url,bb_slug,bb_branch,oci_ocr_target_repo,oci_ocr_target_url,bb_commit_message):
        try:
            logging.getLogger().info(f"Proceeding with git branch as {bb_branch}")
            repo = Repo.clone_from(bb_url,self.target_dir)
            repo.config_writer().set_value("user", "name", bb_user).release()
            repo.config_writer().set_value("user", "email", "function@oci.com").release()
            target_repo = repo.create_remote('target',url=oci_ocr_target_url)
            target_repo.push(force=True)
           

        except Exception as error:
            logging.getLogger().error('Exception' + str (error)) 

def handler(ctx, data: io.BytesIO=None):
    try:
        body = json.loads(data.getvalue())
        if body['test']:
            logging.getLogger().info(f"Its a test {str(body)}")
            raise Exception 
        bb_user = body['actor']['display_name'].replace(" ", "")
        bb_url = body['push']['changes'][0]['new']['links']['html']['href']
        bb_repo_name = bb_url.split("/")[-3]
        bb_branch = body['push']['changes'][0]['new']['name']
        bb_slug = body['repository']['workspace']['slug']
        bb_commit_message = body['push']['changes'][0]['new']['target']['summary']['raw'].replace("\n", "")
        oci_ocr_user_id=os.environ['oci_ocr_user_id']
        oci_ocr_password_id=os.environ['oci_ocr_password_id']
        oci_region = os.environ['oci_region']
        oci_tenacy_namespace = os.environ['oci_tenacy_namespace']
        oci_ocr_project = os.environ['oci_ocr_project']

        secrets_object = secrets_action(oci_region)
        oci_ocrpassword,oci_ocruser = secrets_object.read_secrets(oci_ocr_user_id,oci_ocr_password_id)

        oci_ocr_user = urllib.parse.quote(oci_ocruser,safe="")
        oci_ocr_password = urllib.parse.quote(oci_ocrpassword,safe="")

        oci_ocr_target_repo = f"https://devops.scmservice.{oci_region}.oci.oraclecloud.com/namespaces/{oci_tenacy_namespace}/projects/{oci_ocr_project}/repositories/{bb_repo_name}"
        oci_ocr_target_url= f"https://{oci_ocr_user}:{oci_ocr_password}@devops.scmservice.{oci_region}.oci.oraclecloud.com/namespaces/{oci_tenacy_namespace}/projects/{oci_ocr_project}/repositories/{bb_repo_name}"
        
        logging.getLogger().info(f"User - {bb_user},Url - {bb_url},User - {bb_slug},Commit - {bb_commit_message},Oracle User - {oci_ocr_user},Target Repo - {oci_ocr_target_repo}")
        git_object = git_actions()
        git_object.git_clone(bb_user,bb_url,bb_slug,bb_branch,oci_ocr_target_repo,oci_ocr_target_url,bb_commit_message)

        logging.getLogger().info("Invoked function with default  image")
        return response.Response(
            ctx, 
            response_data=json.dumps({"status": "Hello World! with DefaultImage"}),
            headers={"Content-Type": "application/json"})
    except Exception as error:
        logging.getLogger().error("Exception" + str(error))
    