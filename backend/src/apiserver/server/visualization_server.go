package server

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/kubeflow/pipelines/backend/api/go_client"
	"github.com/kubeflow/pipelines/backend/src/apiserver/resource"
	"github.com/kubeflow/pipelines/backend/src/common/util"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"
)

type VisualizationServer struct {
	resourceManager *resource.ResourceManager
	serviceURL      string
}

func (s *VisualizationServer) CreateVisualization(ctx context.Context, request *go_client.CreateVisualizationRequest) (*go_client.Visualization, error) {
	if err := s.validateCreateVisualizationRequest(request); err != nil {
		return nil, err
	}
	// TODO: Add run id to visualization cache key
	// Ignore error and only check for data when obtaining artifact from MinIO.
	data, _ := s.GetArtifactFromMinio(request.Visualization)
	// Check if data exists and the length of data is greater than 0. This is done
	// because MinIO does not return an error if an object does not exist. Instead
	// it returns and empty byte array. It can then be assumed that if an empty
	// byte array is received, the visualization does not exist. This can be
	// assumed because a visualization, regardless of if an output is generated,
	// will always have the template html (roughly 13k loc) when exported by
	// nbcovert.
	if data != nil && len(data) > 0 {
		request.Visualization.Html = string(data)
	} else {
		start := time.Now()
		body, err := s.GenerateVisualizationFromRequest(request)
		if err != nil {
			return nil, err
		}
		request.Visualization.Html = string(body)
		t := time.Now()
		elapsed := t.Sub(start)
		// Only cache visualization if it takes longer than two seconds to generate.
		if elapsed > time.Second * 2 {
			defer s.PutArtifactInMinio(body, request.Visualization)
		}
	}
	return request.Visualization, nil
}

// validateCreateVisualizationRequest ensures that a go_client.Visualization
// object has valid values.
// It returns an error if a go_client.Visualization object does not have valid
// values.
func (s *VisualizationServer) validateCreateVisualizationRequest(request *go_client.CreateVisualizationRequest) error {
	if len(request.Visualization.InputPath) == 0 {
		return util.NewInvalidInputError("A visualization requires an InputPath to be provided. Received %s", request.Visualization.InputPath)
	}
	// Manually set Arguments to empty JSON if nothing is provided. This is done
	// because visualizations such as TFDV and TFMA only require an InputPath to
	// provided for a visualization to be generated. If no JSON is provided
	// json.Valid will fail without this check as an empty string is provided for
	// those visualizations.
	if len(request.Visualization.Arguments) == 0 {
		request.Visualization.Arguments = "{}"
	}
	if !json.Valid([]byte(request.Visualization.Arguments)) {
		return util.NewInvalidInputError("A visualization requires valid JSON to be provided as Arguments. Received %s", request.Visualization.Arguments)
	}
	return nil
}

// getArgumentsAsJSONFromRequest will convert the values within a
// go_client.CreateVisualizationRequest object to valid JSON that can be used to
// pass arguments to the python visualization service.
// It returns the generated JSON as an array of bytes and any error that is
// encountered.
func (s *VisualizationServer) getArgumentsAsJSONFromRequest(request *go_client.CreateVisualizationRequest) ([]byte, error) {
	var arguments map[string]interface{}
	if err := json.Unmarshal([]byte(request.Visualization.Arguments), &arguments); err != nil {
		return nil, util.Wrap(err, "Unable to parse provided JSON.")
	}
	args, err := json.Marshal(arguments)
	if err != nil {
		return nil, util.Wrap(err, "Unable to compose provided JSON as string.")
	}
	return args, nil
}

// createPythonArgumentsFromRequest converts the values within a
// go_client.CreateVisualizationRequest object to those expected by the python
// visualization service.
// It returns the converted values as a string and any error that is
// encountered.
func (s *VisualizationServer) createPythonArgumentsFromRequest(request *go_client.CreateVisualizationRequest) (string, error) {
	visualizationType := strings.ToLower(go_client.Visualization_Type_name[int32(request.Visualization.Type)])
	arguments, err := s.getArgumentsAsJSONFromRequest(request)
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("--type %s --input_path '%s' --arguments '%s'", visualizationType, request.Visualization.InputPath, arguments), nil
}

// GenerateVisualizationFromRequest communicates with the python visualization
// service to generate HTML visualizations from a request.
// It returns the generated HTML as a string and any error that is encountered.
func (s *VisualizationServer) GenerateVisualizationFromRequest(request *go_client.CreateVisualizationRequest) ([]byte, error) {
	arguments, err := s.createPythonArgumentsFromRequest(request)
	if err != nil {
		return nil, err
	}
	resp, err := http.PostForm(s.serviceURL, url.Values{"arguments": {arguments}})
	if err != nil {
		return nil, util.Wrap(err, "Unable to initialize visualization request.")
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf(resp.Status)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, util.Wrap(err, "Unable to parse visualization response.")
	}
	return body, nil
}

func (s *VisualizationServer) GetArtifactFromMinio(visualization *go_client.Visualization) ([]byte, error) {
	return s.resourceManager.GetVisualizationFromArtifactStore(visualization)
}

func (s *VisualizationServer) PutArtifactInMinio(artifactData []byte, visualization *go_client.Visualization) error {
	return s.resourceManager.PutVisualizationInArtifactStore(artifactData, visualization)
}

func NewVisualizationServer(resourceManager *resource.ResourceManager) *VisualizationServer {
	return &VisualizationServer{resourceManager: resourceManager, serviceURL: "http://visualization-service.kubeflow"}
}
