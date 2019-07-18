package server

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/kubeflow/pipelines/backend/api/go_client"
	"github.com/kubeflow/pipelines/backend/src/apiserver/resource"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
)

type VisualizationServer struct {
	resourceManager *resource.ResourceManager
}

func (VisualizationServer) CreateVisualization(ctx context.Context, request *go_client.CreateVisualizationRequest) (*go_client.Visualization, error) {
	if len(request.Visualization.InputPath) == 0 {
		return nil, errors.New("missing inputPath")
	} else if len(request.Visualization.Arguments) == 0 {
		// Set Arguments to be empty JSON if no Arguments are provided.
		request.Visualization.Arguments = "{}"
	}
	if !json.Valid([]byte(request.Visualization.Arguments)) {
		return nil, errors.New("invalid arguments, arguments must be valid json")
	}
	var arguments map[string]interface{}
	if err := json.Unmarshal([]byte(request.Visualization.Arguments), &arguments); err != nil {
		return nil, err
	}
	arguments["input_path"] = request.Visualization.InputPath
	args, err := json.Marshal(arguments)
	if err != nil {
		return nil, err
	}
	var visualizationType = strings.ToLower(go_client.Visualization_Type_name[int32(request.Visualization.Type)])
	pythonArguments := fmt.Sprintf("--type %s --arguments '%s'", visualizationType, args)
	resp, err := http.PostForm("http://visualization-service.kubeflow", url.Values{"arguments": { pythonArguments }})
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		request.Visualization.Error = err.Error()
		return request.Visualization, err
	}
	request.Visualization.Html = string(body)
	return request.Visualization, nil
}

func NewVisualizationServer(resourceManager *resource.ResourceManager) *VisualizationServer {
	return &VisualizationServer{resourceManager: resourceManager}
}