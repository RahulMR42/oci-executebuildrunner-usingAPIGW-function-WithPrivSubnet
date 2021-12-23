A sample illustration of API Gateay with Function to invoke a build pipeline using Bit Bucket Webhook under a complte PRIVATE Subneted VCN.

-----------
🔔  Objective :

-   Its an illustration to invoke a OCI devops build pipeline using API Gateway and OCI Functions with Bitbucket.

- It is exclusive for Private subnetd ,for Public Subnet you can refer here - https://github.com/RahulMR42/oci-apigateway-function-webhook 

ℹ️  Summary of  Interactions

- Trigger of webhook from Bitbucket based on a push or commit.
- OCI API Gateway gets invoked and intern trigger an OCI Functions.
- OCI Function will fetch the contect from Bitbucket repo and update the OCI Code Repo.
- OCI Devops trigger will be invoked and a build pipeline will be triggered.

![](./images/flow_major.svg)

🗨️ How to Setup (You may skip /refer document according to your environment).


📗 Setup your OCI VCN

----------------------

- Create a VCN using VCN Create wizard. 
- Select a public and private subnet 

![](images/priv_vcn.png)


📗 OCI Vault

----------------

- Create or use an existing Vault - https://docs.oracle.com/en-us/iaas/Content/KeyManagement/home.htm.

- Setup secrets oci_ocr_user & oci_ocr_password 

- Ensure to setup the exact username and password that can be used to interact with OCI Code repo.

- Code repo reference for read. - https://docs.oracle.com/en-us/iaas/Content/devops/using/managing_coderepo.htm 

![](images/priv_vault_secrets.png)


📗 OCI Function

----------------

-   Login to cloudshell or an OCI operator instance or your local machine where you have access to OCI.

- Clone the repo.

```
$ git clone https://github.com/RahulMR42/oci-executebuildrunner-usingAPIGW-function-WithPrivSubnet

```

- Create an OCI Function application - https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatingapps.htm#Creating_Applications 

- Ensure to select the Private subnet for your application.

![](images/priv_fn_applications.png)

- Update your local machine / or cloud shell or operator with Application context (using getting started).
- Refer the documentation or quick start via the console to set the all the contexts.
- Create an OCI Dynamic group to consider all the function objects inside the compartment

```
resource.type = 'fnfunc'
resource.compartment.id = 'ocid1.compartment.oc1..xx'

```
![](images/priv_dg_functions.png)

- Build the functions with the custom code.
- Update func.yaml the OCID of secrets oci_ocr_user_id & oci_ocr_password_id .
- Update the func.yaml with your devops project /tenacy 

```
$ cd oci-apigateway-function-webhook 
$ fn deploy -v --app <application name>

```

- Create a policy for function to read vault secrets,with below policy statements.

```
allow dynamic-group <fn dg name> to manage secret-family in compartment <compartment name>	
allow dynamic-group <fn dg name> to manage secret-family in compartment <compartment name>
allow dynamic-group <fn dg name> to manage vault in compartment <compartment name>	
allow dynamic-group <fn dg name> to manage vault in compartment <compartment name>
allow dynamic-group <fn dg name> to manage keys in compartment <compartment name>
```
![](images/priv_policy_fn_secrets.png)


- Enable logging of function application via the console.

![](images/priv_fn_apps_logs.png)


📗 OCI Gateway

---------

- Create an OCI Gateway https://docs.oracle.com/en-us/iaas/Content/APIGateway/home.htm 
- Ensure to use the private subnet /appropritate security lists.

![](images/priv_gateway.png)

- Create a new deployment ,do basic configurations 

![](images/gw_deploy_basic.png)

- Use CORS and Rate limit ,you may add additional CORS or or filter later.

- Add gateway deployment route type as function ,set the values as accordingly.

```
- method : GET & POST 
- A route value (path)
- Select Oracle functions > Application name > Function name
```

![](images/priv_gw_deploy_1.png)

- Use CORS or headers according to the need /it can be added later also.

![](images/priv_gw_deploy_2.png)

- Add a route / select HTTP methods as GET/POST.
- Select oracle functions and with the necessary values 

![](images/priv_gw_deploy_3.png)

- Create a dynamic group refering to the Gateway with below rules.

```
ALL {resource.type = 'ApiGateway', resource.compartment.id = 'ocid1.compartment.oc1..xx'}
```

![](images/priv_dg_gateway.png)

- Create a policy for gateway dynamic group to access the OCI Functions with below policy statements.

```
Allow dynamic-group <dg-api-gateway> to use functions-family in compartment <compartment name>
```

📗 Update VCN to allow the gateway access 

---------

- Add a new Ingress rule to the PRIVATE subnet for the VCN

![](images/priv_vcn_sl_ingress.png)


📗 OCI DEVOPS CODE Repo

---------

- Create a devops project / A Code repo - https://docs.oracle.com/en-us/iaas/Content/devops/using/managing_coderepo.htm 

- This will be the repo that we will be using with OCI ecosystem for the sample build runner.

- Use the same name as that of bitbucket repo (Will be created in the further steps).

![](images/priv_coderepo.png)


📗 Bastion for Private instance access (Optional for a quick test)

---------

- To do a test ,let us create a instance for them private subnet network.
- Ensure to enable bastion agent for the host.

![](images/priv_instance_1.png)

![](images/priv_instance_2.png)


- Create a bastion using the same private subnet.
- You may use 0.0.0.0/0 or exact subnet or both as the allowed CIDR.

![](images/priv_bastion_cidr.png)

- Update the subnet VCN to allow the access to bastion,for the make a note of the private IP of the bastion service.

![](images/priv_ingress_vcn_rule.png)


Do a Quick tests now (Optional).

---------

- For sure it wont server the purpose ,but it will ensure that from the private subnet instance we are able to access the gateway.

- Create an SSH session using Bastion Sessions.

![](images/priv_bastion_session.png)

- Select the test instance we created in the above steps.
- Once the session is reay ,copy the SSH and replace the actual values.Sample format would look like.

```
ssh -i <PRIVATE KEY PATH> -N -L 8080:<PRIV IP of the Instance>:22 -p 22 ocid1.bastionsession.oc1.xxxx@host.bastion.xxx.oci.oraclecloud.com
```

- Invoke the command on your local shell by replacing the PATH.
- Once the session is established (It will open a session and keep with out any messages),do a ssh using opc user and login to the instance.

![](images/priv_port_forward1.png)

- With out closing the current prompt opern another prompt on the same machine.
- Ensure you are on the right path where you have the private key or provide the aboslute path.
- Also ensure the key has a permisson of 600 (unix model) on the machine.

![](images/priv_session_instance.png)

- From the instance invoke the Gatway deployment URL.
- To have the URL go to Gatway>Deployment ,copy the endpoint and add it with the custom route we have mentioned .

```
curl -k https://xxxx.apigateway.eu-frankfurt-1.oci.customer-oci.com/v0/devopstrigger -d '{"host":"'`hostname`'"}' -X POST
```

- Validate the execution via Application > Logs >FN invoke logs.
- You should see something as below 

![](images/priv_test_logs.png)

- For an error or unreachable case ,check your VCN , URL , Security lists ,Function application netwrok etc .



📗 Bitbucket Setups

---------

- Create a bitbucket repo,with in the bitbucket hosted in the priv VCN.
- Push the content to bitbucket for tests Or you can upload manually ,ensure to have build_spec.yaml file.

- You can use the instane we created and bastion for such operations over https.

```
git remote add bitbucket <bitbucket reference>
git push bitbucket main:main 
```
![](images/bitbucket_repo.png)

- Create a webhook using API gateway URL (It must be absolute url with path prefix etc).

![](images/bitbucket_webhook.png)




📗 5 - Create a test OCI Build pipeliine/stage

---------

- Create a build pipeline in the same OCI devops project.

![](images/buildpipeline.png)

- Add a build stage with manage build type and the OCI Repo.

![](images/build_stage.png)


- Create a OCI trigger with the repo and the build pipeline.

![](images/trigger.png)

- Refer the document for all the policies https://docs.oracle.com/en-us/iaas/Content/devops/using/managing_build_pipelines.htm.


📗 7 - Tests

--------

All set !!! Lets test .

- touch a dummy file & push to bitbucket from the test instance.

```
$ Go to the cloned folder.
$ echo "test" >test.txt
$ git add -A;git commit -m "test to bb"
$ git push bitbucket main:main
```

- Validate the webhook execution via bitbucket ui.

![](images/test_webhooks.png)

- Validate the build pipeline /it must be executed automatically 

![](images/build_history.png)

![](images/build_stage_details.png)

- You can refer the OCI code repo and validate the commits details as well .

![](images/commit.png)

- For any errors or details ,refer the functions logs via Application > Logs  .

![](images/function_logs.png)


🎵 Tail end 

- You can add /restrict access with ratelimit / tls / or explcit control inside the function (like allow only if the incommig user is part of alist from vault ) etc .

- You can additional Network Security Groups etc.