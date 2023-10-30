# robocorp-workspace
Robocorp Control Room API

The `robocorp.workspace` package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 1.0
- Package version: 0.1.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.7+

## Installation & Usage

This python library package is generated without supporting files like setup.py or requirements files

To be able to use it, you will need these dependencies in your own package that uses this library:

* urllib3 >= 1.25.3
* python-dateutil
* pydantic
* aenum

## Getting Started

In your own code, to use this library to connect and interact with robocorp-workspace,
you can run the following:

```python

import time
import robocorp.workspace
from robocorp.workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = robocorp.workspace.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: API Key with permissions
configuration.api_key['API Key with permissions'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['API Key with permissions'] = 'Bearer'


# Enter a context with an instance of the API client
with robocorp.workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = robocorp.workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker should reside.
    update_worker_request = robocorp.workspace.UpdateWorkerRequest() # UpdateWorkerRequest | 

    try:
        # Create new asset
        api_response = api_instance.create_asset(workspace_id, update_worker_request)
        print("The response of AssetApi->create_asset:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AssetApi->create_asset: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AssetApi* | [**create_asset**](robocorp/workspace/docs/AssetApi.md#create_asset) | **POST** /workspaces/{workspace_id}/assets | Create new asset
*AssetApi* | [**create_asset_upload**](robocorp/workspace/docs/AssetApi.md#create_asset_upload) | **POST** /workspaces/{workspace_id}/assets/{asset_id}/uploads | Create asset upload
*AssetApi* | [**delete_asset**](robocorp/workspace/docs/AssetApi.md#delete_asset) | **DELETE** /workspaces/{workspace_id}/assets/{asset_id} | Delete asset
*AssetApi* | [**get_asset**](robocorp/workspace/docs/AssetApi.md#get_asset) | **GET** /workspaces/{workspace_id}/assets/{asset_id} | Get asset
*AssetApi* | [**get_asset_upload**](robocorp/workspace/docs/AssetApi.md#get_asset_upload) | **GET** /workspaces/{workspace_id}/assets/{asset_id}/uploads/{upload_id} | Get asset upload
*AssetApi* | [**list_assets**](robocorp/workspace/docs/AssetApi.md#list_assets) | **GET** /workspaces/{workspace_id}/assets | List assets
*AssistantApi* | [**create_assistant**](robocorp/workspace/docs/AssistantApi.md#create_assistant) | **POST** /workspaces/{workspace_id}/assistants | Create assistant
*AssistantApi* | [**get_assistant**](robocorp/workspace/docs/AssistantApi.md#get_assistant) | **GET** /workspaces/{workspace_id}/assistants/{assistant_id} | Get assistant
*AssistantApi* | [**get_assistant_run**](robocorp/workspace/docs/AssistantApi.md#get_assistant_run) | **GET** /workspaces/{workspace_id}/assistant-runs/{assistant_run_id} | Get assistant run
*AssistantApi* | [**list_assistant_runs**](robocorp/workspace/docs/AssistantApi.md#list_assistant_runs) | **GET** /workspaces/{workspace_id}/assistant-runs | List assistant runs
*AssistantApi* | [**list_assistants**](robocorp/workspace/docs/AssistantApi.md#list_assistants) | **GET** /workspaces/{workspace_id}/assistants | List assistants
*ProcessApi* | [**list_processes**](robocorp/workspace/docs/ProcessApi.md#list_processes) | **GET** /workspaces/{workspace_id}/processes | List processes
*ProcessRunApi* | [**delete_process_run**](robocorp/workspace/docs/ProcessRunApi.md#delete_process_run) | **DELETE** /workspaces/{workspace_id}/process-runs/{process_run_id} | Delete process run
*ProcessRunApi* | [**get_process_run**](robocorp/workspace/docs/ProcessRunApi.md#get_process_run) | **GET** /workspaces/{workspace_id}/process-runs/{process_run_id} | Get process run
*ProcessRunApi* | [**list_process_run_outputs**](robocorp/workspace/docs/ProcessRunApi.md#list_process_run_outputs) | **GET** /workspaces/{workspace_id}/outputs | List process run outputs
*ProcessRunApi* | [**list_process_runs**](robocorp/workspace/docs/ProcessRunApi.md#list_process_runs) | **GET** /workspaces/{workspace_id}/process-runs | List process runs
*ProcessRunApi* | [**start_process_run**](robocorp/workspace/docs/ProcessRunApi.md#start_process_run) | **POST** /workspaces/{workspace_id}/processes/{process_id}/process-runs | Start process run
*ProcessRunApi* | [**start_process_run_qs_auth**](robocorp/workspace/docs/ProcessRunApi.md#start_process_run_qs_auth) | **POST** /workspaces/{workspace_id}/processes/{process_id}/process-runs-integrations | Start process run (for integrations)
*ProcessRunApi* | [**stop_process_run**](robocorp/workspace/docs/ProcessRunApi.md#stop_process_run) | **POST** /workspaces/{workspace_id}/process-runs/{process_run_id}/stop | Stop process run
*StepRunApi* | [**get_step_run**](robocorp/workspace/docs/StepRunApi.md#get_step_run) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id} | Get step run
*StepRunApi* | [**get_step_run_artifact**](robocorp/workspace/docs/StepRunApi.md#get_step_run_artifact) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/artifacts/{artifact_id} | Get step run artifact
*StepRunApi* | [**list_step_run_artifacts**](robocorp/workspace/docs/StepRunApi.md#list_step_run_artifacts) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/artifacts | List step run artifacts
*StepRunApi* | [**list_step_run_console_messages**](robocorp/workspace/docs/StepRunApi.md#list_step_run_console_messages) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/console-messages | List step run console messages
*StepRunApi* | [**list_step_run_events**](robocorp/workspace/docs/StepRunApi.md#list_step_run_events) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/events | List step run events
*StepRunApi* | [**list_step_runs**](robocorp/workspace/docs/StepRunApi.md#list_step_runs) | **GET** /workspaces/{workspace_id}/step-runs | List step runs
*TaskPackageApi* | [**create_task_package**](robocorp/workspace/docs/TaskPackageApi.md#create_task_package) | **POST** /workspaces/{workspace_id}/task-packages | Create new task package
*TaskPackageApi* | [**delete_task_package**](robocorp/workspace/docs/TaskPackageApi.md#delete_task_package) | **DELETE** /workspaces/{workspace_id}/task-packages/{task_package_id} | Delete task package
*TaskPackageApi* | [**get_task_package**](robocorp/workspace/docs/TaskPackageApi.md#get_task_package) | **GET** /workspaces/{workspace_id}/task-packages/{task_package_id} | Get task package
*WebhooksApi* | [**create_webhook**](robocorp/workspace/docs/WebhooksApi.md#create_webhook) | **POST** /workspaces/{workspace_id}/webhooks | Create Process webhook
*WebhooksApi* | [**delete_webhook**](robocorp/workspace/docs/WebhooksApi.md#delete_webhook) | **DELETE** /workspaces/{workspace_id}/webhooks/{webhook_id} | Delete webhook
*WebhooksApi* | [**get_webhook**](robocorp/workspace/docs/WebhooksApi.md#get_webhook) | **GET** /workspaces/{workspace_id}/webhooks/{webhook_id} | Get Webhook
*WebhooksApi* | [**list_webhooks**](robocorp/workspace/docs/WebhooksApi.md#list_webhooks) | **GET** /workspaces/{workspace_id}/webhooks | List Webhooks
*WorkItemApi* | [**create_work_item**](robocorp/workspace/docs/WorkItemApi.md#create_work_item) | **POST** /workspaces/{workspace_id}/work-items | Create work item
*WorkItemApi* | [**create_work_item_file**](robocorp/workspace/docs/WorkItemApi.md#create_work_item_file) | **POST** /workspaces/{workspace_id}/work-items/{work_item_id}/files | Create work item file
*WorkItemApi* | [**get_work_item**](robocorp/workspace/docs/WorkItemApi.md#get_work_item) | **GET** /workspaces/{workspace_id}/work-items/{work_item_id} | Get work item
*WorkItemApi* | [**list_work_items**](robocorp/workspace/docs/WorkItemApi.md#list_work_items) | **GET** /workspaces/{workspace_id}/work-items | List work items
*WorkItemApi* | [**run_work_item_batch_operation**](robocorp/workspace/docs/WorkItemApi.md#run_work_item_batch_operation) | **POST** /workspaces/{workspace_id}/work-items/batch | Retry, delete or mark work items as done
*WorkItemApi* | [**update_work_item_payload**](robocorp/workspace/docs/WorkItemApi.md#update_work_item_payload) | **POST** /workspaces/{workspace_id}/work-items/{work_item_id}/payload | Update work item payload
*WorkerApi* | [**create_link_token**](robocorp/workspace/docs/WorkerApi.md#create_link_token) | **POST** /workspaces/{workspace_id}/workers/link-tokens | Create worker link token
*WorkerApi* | [**delete_worker**](robocorp/workspace/docs/WorkerApi.md#delete_worker) | **DELETE** /workspaces/{workspace_id}/workers/{worker_id} | Delete worker
*WorkerApi* | [**get_worker**](robocorp/workspace/docs/WorkerApi.md#get_worker) | **GET** /workspaces/{workspace_id}/workers/{worker_id} | Get worker
*WorkerApi* | [**list_workers**](robocorp/workspace/docs/WorkerApi.md#list_workers) | **GET** /workspaces/{workspace_id}/workers | List workers
*WorkerApi* | [**update_worker**](robocorp/workspace/docs/WorkerApi.md#update_worker) | **POST** /workspaces/{workspace_id}/workers/{worker_id} | Update worker
*WorkerGroupApi* | [**add_worker_to_group**](robocorp/workspace/docs/WorkerGroupApi.md#add_worker_to_group) | **POST** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/workers | Add worker to worker group
*WorkerGroupApi* | [**create_worker_group**](robocorp/workspace/docs/WorkerGroupApi.md#create_worker_group) | **POST** /workspaces/{workspace_id}/worker-groups | Create worker group
*WorkerGroupApi* | [**create_worker_group_link_token**](robocorp/workspace/docs/WorkerGroupApi.md#create_worker_group_link_token) | **POST** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens | Create worker group link token
*WorkerGroupApi* | [**delete_worker_group**](robocorp/workspace/docs/WorkerGroupApi.md#delete_worker_group) | **DELETE** /workspaces/{workspace_id}/worker-groups/{worker_group_id} | Delete worker group
*WorkerGroupApi* | [**delete_worker_group_link_token**](robocorp/workspace/docs/WorkerGroupApi.md#delete_worker_group_link_token) | **DELETE** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens/{link_token_id} | Delete worker group link token
*WorkerGroupApi* | [**get_worker_group**](robocorp/workspace/docs/WorkerGroupApi.md#get_worker_group) | **GET** /workspaces/{workspace_id}/worker-groups/{worker_group_id} | Get worker group
*WorkerGroupApi* | [**get_worker_group_link_token**](robocorp/workspace/docs/WorkerGroupApi.md#get_worker_group_link_token) | **GET** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens/{link_token_id} | Get worker group link token
*WorkerGroupApi* | [**list_worker_group_link_tokens**](robocorp/workspace/docs/WorkerGroupApi.md#list_worker_group_link_tokens) | **GET** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens | List worker group link tokens
*WorkerGroupApi* | [**list_worker_groups**](robocorp/workspace/docs/WorkerGroupApi.md#list_worker_groups) | **GET** /workspaces/{workspace_id}/worker-groups | List worker groups
*WorkerGroupApi* | [**remove_worker_from_group**](robocorp/workspace/docs/WorkerGroupApi.md#remove_worker_from_group) | **DELETE** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/workers/{worker_id} | Remove worker from worker group
*WorkerGroupApi* | [**update_worker_group**](robocorp/workspace/docs/WorkerGroupApi.md#update_worker_group) | **POST** /workspaces/{workspace_id}/worker-groups/{worker_group_id} | Update worker group
*WorkerGroupApi* | [**update_worker_group_link_token**](robocorp/workspace/docs/WorkerGroupApi.md#update_worker_group_link_token) | **POST** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens/{link_token_id} | Update worker group link token
*WorkspaceApi* | [**get_workspace**](robocorp/workspace/docs/WorkspaceApi.md#get_workspace) | **GET** /workspaces/{workspace_id} | Get workspace


## Documentation For Models

 - [ActivityResource](robocorp/workspace/docs/ActivityResource.md)
 - [ActivityRunResource](robocorp/workspace/docs/ActivityRunResource.md)
 - [AddWorkerToGroupRequest](robocorp/workspace/docs/AddWorkerToGroupRequest.md)
 - [AddWorkerToGroupRequestWorker](robocorp/workspace/docs/AddWorkerToGroupRequestWorker.md)
 - [AnyValidJson](robocorp/workspace/docs/AnyValidJson.md)
 - [AnyValidJsonOptional](robocorp/workspace/docs/AnyValidJsonOptional.md)
 - [AssetDetailsResource](robocorp/workspace/docs/AssetDetailsResource.md)
 - [AssetDetailsResourcePayload](robocorp/workspace/docs/AssetDetailsResourcePayload.md)
 - [AssetPayloadDataResource](robocorp/workspace/docs/AssetPayloadDataResource.md)
 - [AssetPayloadEmptyResource](robocorp/workspace/docs/AssetPayloadEmptyResource.md)
 - [AssetPayloadUrlResource](robocorp/workspace/docs/AssetPayloadUrlResource.md)
 - [AssetResource](robocorp/workspace/docs/AssetResource.md)
 - [AssetUploadCompletedResource](robocorp/workspace/docs/AssetUploadCompletedResource.md)
 - [AssetUploadCreatedResource](robocorp/workspace/docs/AssetUploadCreatedResource.md)
 - [AssetUploadCreatedResourceWithUrl](robocorp/workspace/docs/AssetUploadCreatedResourceWithUrl.md)
 - [AssetUploadFailedResource](robocorp/workspace/docs/AssetUploadFailedResource.md)
 - [AssetUploadPendingResource](robocorp/workspace/docs/AssetUploadPendingResource.md)
 - [AssetUploadResource](robocorp/workspace/docs/AssetUploadResource.md)
 - [AssistantResource](robocorp/workspace/docs/AssistantResource.md)
 - [AssistantResourceTask](robocorp/workspace/docs/AssistantResourceTask.md)
 - [AssistantRunResource](robocorp/workspace/docs/AssistantRunResource.md)
 - [AssistantRunResourceError](robocorp/workspace/docs/AssistantRunResourceError.md)
 - [CreateAssetUpload200Response](robocorp/workspace/docs/CreateAssetUpload200Response.md)
 - [CreateAssetUploadRequest](robocorp/workspace/docs/CreateAssetUploadRequest.md)
 - [CreateAssistantRequest](robocorp/workspace/docs/CreateAssistantRequest.md)
 - [CreateAssistantRequestTask](robocorp/workspace/docs/CreateAssistantRequestTask.md)
 - [CreateLinkTokenRequest](robocorp/workspace/docs/CreateLinkTokenRequest.md)
 - [CreateTaskPackageRequest](robocorp/workspace/docs/CreateTaskPackageRequest.md)
 - [CreateWorkItemFile200Response](robocorp/workspace/docs/CreateWorkItemFile200Response.md)
 - [CreateWorkItemFile200ResponseUpload](robocorp/workspace/docs/CreateWorkItemFile200ResponseUpload.md)
 - [CreateWorkItemFileRequest](robocorp/workspace/docs/CreateWorkItemFileRequest.md)
 - [CreateWorkItemRequest](robocorp/workspace/docs/CreateWorkItemRequest.md)
 - [CreateWorkerGroupLinkTokenRequest](robocorp/workspace/docs/CreateWorkerGroupLinkTokenRequest.md)
 - [DeleteWorker200Response](robocorp/workspace/docs/DeleteWorker200Response.md)
 - [EmptyAssetDetailsResource](robocorp/workspace/docs/EmptyAssetDetailsResource.md)
 - [EmptyAssetDetailsResourcePayload](robocorp/workspace/docs/EmptyAssetDetailsResourcePayload.md)
 - [GenericErrorResponse](robocorp/workspace/docs/GenericErrorResponse.md)
 - [GenericErrorResponseError](robocorp/workspace/docs/GenericErrorResponseError.md)
 - [GetAssistant200Response](robocorp/workspace/docs/GetAssistant200Response.md)
 - [GetStepRunArtifact200Response](robocorp/workspace/docs/GetStepRunArtifact200Response.md)
 - [LinkTokenResource](robocorp/workspace/docs/LinkTokenResource.md)
 - [ListAssets200Response](robocorp/workspace/docs/ListAssets200Response.md)
 - [ListAssets200ResponseDataInner](robocorp/workspace/docs/ListAssets200ResponseDataInner.md)
 - [ListAssistantRuns200Response](robocorp/workspace/docs/ListAssistantRuns200Response.md)
 - [ListAssistants200Response](robocorp/workspace/docs/ListAssistants200Response.md)
 - [ListProcessRunOutputs200Response](robocorp/workspace/docs/ListProcessRunOutputs200Response.md)
 - [ListProcessRuns200Response](robocorp/workspace/docs/ListProcessRuns200Response.md)
 - [ListProcesses200Response](robocorp/workspace/docs/ListProcesses200Response.md)
 - [ListProcesses200ResponseDataInner](robocorp/workspace/docs/ListProcesses200ResponseDataInner.md)
 - [ListStepRunArtifacts200Response](robocorp/workspace/docs/ListStepRunArtifacts200Response.md)
 - [ListStepRunArtifacts200ResponseDataInner](robocorp/workspace/docs/ListStepRunArtifacts200ResponseDataInner.md)
 - [ListStepRunConsoleMessages200Response](robocorp/workspace/docs/ListStepRunConsoleMessages200Response.md)
 - [ListStepRunConsoleMessages200ResponseDataInner](robocorp/workspace/docs/ListStepRunConsoleMessages200ResponseDataInner.md)
 - [ListStepRunEvents200Response](robocorp/workspace/docs/ListStepRunEvents200Response.md)
 - [ListStepRunEvents200ResponseDataInner](robocorp/workspace/docs/ListStepRunEvents200ResponseDataInner.md)
 - [ListStepRuns200Response](robocorp/workspace/docs/ListStepRuns200Response.md)
 - [ListWebhooks200Response](robocorp/workspace/docs/ListWebhooks200Response.md)
 - [ListWebhooks200ResponseDataInner](robocorp/workspace/docs/ListWebhooks200ResponseDataInner.md)
 - [ListWebhooks200ResponseDataInnerProcess](robocorp/workspace/docs/ListWebhooks200ResponseDataInnerProcess.md)
 - [ListWorkItems200Response](robocorp/workspace/docs/ListWorkItems200Response.md)
 - [ListWorkerGroupLinkTokens200Response](robocorp/workspace/docs/ListWorkerGroupLinkTokens200Response.md)
 - [ListWorkerGroups200Response](robocorp/workspace/docs/ListWorkerGroups200Response.md)
 - [ListWorkers200Response](robocorp/workspace/docs/ListWorkers200Response.md)
 - [PaginationDetails](robocorp/workspace/docs/PaginationDetails.md)
 - [ProcessReferenceResource](robocorp/workspace/docs/ProcessReferenceResource.md)
 - [ProcessRunCallback](robocorp/workspace/docs/ProcessRunCallback.md)
 - [ProcessRunOutputResource](robocorp/workspace/docs/ProcessRunOutputResource.md)
 - [ProcessRunReferenceResource](robocorp/workspace/docs/ProcessRunReferenceResource.md)
 - [ProcessRunResource](robocorp/workspace/docs/ProcessRunResource.md)
 - [ProcessRunResourceStartedBy](robocorp/workspace/docs/ProcessRunResourceStartedBy.md)
 - [ProcessRunResourceStartedByDetails](robocorp/workspace/docs/ProcessRunResourceStartedByDetails.md)
 - [ProcessWebhookPayload](robocorp/workspace/docs/ProcessWebhookPayload.md)
 - [RunWorkItemBatchOperationRequest](robocorp/workspace/docs/RunWorkItemBatchOperationRequest.md)
 - [StartProcessRun200Response](robocorp/workspace/docs/StartProcessRun200Response.md)
 - [StartProcessRun200ResponseOneOf](robocorp/workspace/docs/StartProcessRun200ResponseOneOf.md)
 - [StartProcessRunQsAuth200Response](robocorp/workspace/docs/StartProcessRunQsAuth200Response.md)
 - [StartProcessRunRequest](robocorp/workspace/docs/StartProcessRunRequest.md)
 - [StartProcessRunRequestOneOf](robocorp/workspace/docs/StartProcessRunRequestOneOf.md)
 - [StartProcessRunRequestOneOf1](robocorp/workspace/docs/StartProcessRunRequestOneOf1.md)
 - [StartProcessRunRequestOneOf2](robocorp/workspace/docs/StartProcessRunRequestOneOf2.md)
 - [StartProcessRunRequestOneOf3](robocorp/workspace/docs/StartProcessRunRequestOneOf3.md)
 - [StepRunResource](robocorp/workspace/docs/StepRunResource.md)
 - [StepRunResourceError](robocorp/workspace/docs/StepRunResourceError.md)
 - [StopProcessRun200Response](robocorp/workspace/docs/StopProcessRun200Response.md)
 - [StopProcessRunRequest](robocorp/workspace/docs/StopProcessRunRequest.md)
 - [TaskPackageResource](robocorp/workspace/docs/TaskPackageResource.md)
 - [TaskPackageResourceDownload](robocorp/workspace/docs/TaskPackageResourceDownload.md)
 - [UpdateWorkItemPayloadRequest](robocorp/workspace/docs/UpdateWorkItemPayloadRequest.md)
 - [UpdateWorkerRequest](robocorp/workspace/docs/UpdateWorkerRequest.md)
 - [ValidationErrorResponse](robocorp/workspace/docs/ValidationErrorResponse.md)
 - [WebhookResource](robocorp/workspace/docs/WebhookResource.md)
 - [WorkItemException](robocorp/workspace/docs/WorkItemException.md)
 - [WorkItemFile](robocorp/workspace/docs/WorkItemFile.md)
 - [WorkItemFileDownload](robocorp/workspace/docs/WorkItemFileDownload.md)
 - [WorkItemResource](robocorp/workspace/docs/WorkItemResource.md)
 - [WorkItemState](robocorp/workspace/docs/WorkItemState.md)
 - [WorkItemWithoutDataResource](robocorp/workspace/docs/WorkItemWithoutDataResource.md)
 - [WorkerGroupLinkTokenResource](robocorp/workspace/docs/WorkerGroupLinkTokenResource.md)
 - [WorkerGroupResource](robocorp/workspace/docs/WorkerGroupResource.md)
 - [WorkerResource](robocorp/workspace/docs/WorkerResource.md)
 - [WorkerToGroupLinkListing](robocorp/workspace/docs/WorkerToGroupLinkListing.md)
 - [WorkspaceReferenceResource](robocorp/workspace/docs/WorkspaceReferenceResource.md)
 - [WorkspaceResource](robocorp/workspace/docs/WorkspaceResource.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="API Key with permissions"></a>
### API Key with permissions

- **Type**: API key
- **API key parameter name**: Authorization
- **Location**: HTTP header


## Author



