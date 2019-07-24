// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package storage

import (
	"github.com/kubeflow/pipelines/backend/api/go_client"
	"path"
	"strings"
)

const (
	pipelineFolder = "pipelines"
	visualizationFolder = "visualizations"
)

// CreatePipelinePath creates object store path to a pipeline spec.
func CreatePipelinePath(pipelineID string) string {
	return path.Join(pipelineFolder, pipelineID)
}

// CreateVisualizationPath creates object store path to visualization spec.
func CreateVisualizationPath(visualization *go_client.Visualization) string {
	visualizationType := strings.ToLower(go_client.Visualization_Type_name[int32(visualization.Type)])
	cleanInputPath := path.Clean(visualization.InputPath)
	cleanInputPath = strings.ToLower(cleanInputPath)
	cleanInputPath = strings.Replace(cleanInputPath, "/", "_", -1)
	return path.Join(visualizationFolder, visualizationType, cleanInputPath)
}
