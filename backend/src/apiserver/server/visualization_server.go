package server

import (
	"context"
	"errors"
	"fmt"
	"github.com/kubeflow/pipelines/backend/api/go_client"
	"github.com/kubeflow/pipelines/backend/src/apiserver/resource"
	"io/ioutil"
	"net/http"
	"net/url"
)

type VisualizationServer struct {
	resourceManager *resource.ResourceManager
}

func (VisualizationServer) CreateVisualization(ctx context.Context, request *go_client.CreateVisualizationRequest) (*go_client.Visualization, error) {
	if len(request.Visualization.InputPath) == 0 {
		return nil, errors.New("missing inputPath")
	} else if len(request.Visualization.Arguments) == 0 {
		return nil, errors.New("missing arguments")
	}
	arguments := fmt.Sprintf("--predictions %s", request.Visualization.InputPath)
	for _, argument := range request.Visualization.Arguments {
		arguments += fmt.Sprintf(" %s", argument)
	}
	resp, err := http.PostForm("http://visualization-service.kubeflow", url.Values{"arguments": { arguments }})
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	request.Visualization.Html = string(body)
	return request.Visualization, nil
}

func NewVisualizationServer(resourceManager *resource.ResourceManager) *VisualizationServer {
	return &VisualizationServer{resourceManager: resourceManager}
}