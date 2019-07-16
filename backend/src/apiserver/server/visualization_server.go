package server

import (
	"context"
	"github.com/kubeflow/pipelines/backend/api/go_client"
	"github.com/kubeflow/pipelines/backend/src/apiserver/resource"
)

type VisualizationServer struct {
	resourceManager *resource.ResourceManager
}

func (VisualizationServer) CreateVisualization(context.Context, *go_client.CreateVisualizationRequest) (*go_client.Visualization, error) {
	panic("implement me")
}

func NewVisualizationServer(resourceManager *resource.ResourceManager) *VisualizationServer {
	return &VisualizationServer{resourceManager: resourceManager}
}
