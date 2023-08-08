# webhook.py

from flask import Flask, request, abort
import json

app = Flask(__name__)

def is_forbidden_delete(resource_type, resource_name):
    forbidden_resources = [
        {
            "type": "serviceinstances.services.cloud.sap.com",
            "name": "jam-objectstore-sm-service-instance"
        },
        {
            "type": "servicebindings.services.cloud.sap.com",
            "name": "jam-objectstore-sm-service-binding"
        },
        {
            "type": "secrets",
            "name": "jam-objectstore-sm-service-binding"
        }
    ]
    
    for forbidden_resource in forbidden_resources:
        if resource_type == forbidden_resource["type"] and resource_name == forbidden_resource["name"]:
            return True
    return False

@app.route("/validate-delete-resource", methods=["POST"])
def validate_delete_resource():
    admission_request = json.loads(request.data)
    
    # 检查请求类型是否为删除操作
    if admission_request["request"]["operation"] == "DELETE":
        # 获取要删除的资源类型和名称
        resource_type = admission_request["request"]["kind"]["kind"]
        resource_name = admission_request["request"]["name"]
        
        # 检查是否为禁止删除的资源
        if is_forbidden_delete(resource_type, resource_name):
            admission_response = {
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "allowed": False,
                    "status": {
                        "code": 403,
                        "message": "Deleting this resource is not allowed."
                    }
                }
            }
            return json.dumps(admission_response)
    
    # 允许其他操作
    admission_response = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "allowed": True
        }
    }
    return json.dumps(admission_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
