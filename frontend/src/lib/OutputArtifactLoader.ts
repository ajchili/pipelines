/*
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import WorkflowParser, { StoragePath } from './WorkflowParser';
import { Apis } from '../lib/Apis';
import { ConfusionMatrixConfig } from '../components/viewers/ConfusionMatrix';
import { HTMLViewerConfig } from '../components/viewers/HTMLViewer';
import { MarkdownViewerConfig } from '../components/viewers/MarkdownViewer';
import { PagedTableConfig } from '../components/viewers/PagedTable';
import { PlotType, ViewerConfig } from '../components/viewers/Viewer';
import { ROCCurveConfig } from '../components/viewers/ROCCurve';
import { TensorboardViewerConfig } from '../components/viewers/Tensorboard';
import { csvParseRows } from 'd3-dsv';
import { logger, errorToMessage } from './Utils';
import { ApiVisualizationType } from 'src/apis/visualization';

export interface PlotMetadata {
  format?: 'csv';
  header?: string[];
  labels?: string[];
  predicted_col?: string;
  schema?: Array<{ type: string, name: string }>;
  source: string;
  storage?: 'gcs' | 'inline';
  target_col?: string;
  type: PlotType;
}

export interface OutputMetadata {
  outputs: PlotMetadata[];
}

export class OutputArtifactLoader {

  public static async load(outputPath: StoragePath): Promise<ViewerConfig[]> {
    let plotMetadataList: PlotMetadata[] = [];
    try {
      const metadataFile = await Apis.readFile(outputPath);
      if (metadataFile) {
        try {
          plotMetadataList = (JSON.parse(metadataFile) as OutputMetadata).outputs;
          if (plotMetadataList === undefined) {
            throw new Error('"outputs" field required by not found on metadata file');
          }
        } catch (e) {
          logger.error(`Could not parse metadata file at: ${outputPath.key}. Error: ${e}`);
          return [];
        }
      }
    } catch (err) {
      const errorMessage = await errorToMessage(err);
      logger.error('Error loading run outputs:', errorMessage);
      // TODO: error dialog
    }

    const configs: Array<ViewerConfig | null> = await Promise.all(
      plotMetadataList.map(async metadata => {
        switch (metadata.type) {
          case (PlotType.CONFUSION_MATRIX):
            return await this.buildConfusionMatrixConfig(metadata);
          case (PlotType.MARKDOWN):
            return await this.buildMarkdownViewerConfig(metadata);
          case (PlotType.TABLE):
            return await this.buildPythonVisualizationConfig(metadata, ApiVisualizationType.TABLE);
          case (PlotType.TENSORBOARD):
            return await this.buildTensorboardConfig(metadata);
          case (PlotType.WEB_APP):
            return await this.buildHtmlViewerConfig(metadata);
          case (PlotType.ROC):
            return await this.buildPythonVisualizationConfig(metadata, ApiVisualizationType.ROCCURVE);
          default:
            logger.error('Unknown plot type: ' + metadata.type);
            return null;
        }
      })
    );

    return configs.filter(c => !!c) as ViewerConfig[];
  }

  public static async buildConfusionMatrixConfig(metadata: PlotMetadata): Promise<ConfusionMatrixConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    if (!metadata.labels) {
      throw new Error('Malformed metadata, property "labels" is required.');
    }
    if (!metadata.schema) {
      throw new Error('Malformed metadata, property "schema" missing.');
    }
    if (!Array.isArray(metadata.schema)) {
      throw new Error('"schema" must be an array of {"name": string, "type": string} objects');
    }

    const path = WorkflowParser.parseStoragePath(metadata.source);
    const csvRows = csvParseRows((await Apis.readFile(path)).trim());
    const labels = metadata.labels;
    const labelIndex: { [label: string]: number } = {};
    let index = 0;
    labels.forEach((l) => {
      labelIndex[l] = index++;
    });

    if (labels.length ** 2 !== csvRows.length) {
      throw new Error(
        `Data dimensions ${csvRows.length} do not match the number of labels passed ${labels.length}`);
    }

    const data = Array.from(Array(labels.length), () => new Array(labels.length));
    csvRows.forEach(([target, predicted, count]) => {
      const i = labelIndex[target.trim()];
      const j = labelIndex[predicted.trim()];
      data[i][j] = Number.parseInt(count, 10);
    });

    const columnNames = metadata.schema.map((r) => {
      if (!r.name) {
        throw new Error('Each item in the "schema" array must contain a "name" field');
      }
      return r.name;
    });
    const axes = [columnNames[0], columnNames[1]];

    return {
      axes,
      data,
      labels,
      type: PlotType.CONFUSION_MATRIX,
    };
  }

  public static async buildPagedTableConfig(metadata: PlotMetadata): Promise<PagedTableConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    if (!metadata.header) {
      throw new Error('Malformed metadata, property "header" is required.');
    }
    if (!metadata.format) {
      throw new Error('Malformed metadata, property "format" is required.');
    }
    let data: string[][] = [];
    const labels = metadata.header || [];

    switch (metadata.format) {
      case 'csv':
        const path = WorkflowParser.parseStoragePath(metadata.source);
        data = csvParseRows((await Apis.readFile(path)).trim()).map(r => r.map(c => c.trim()));
        break;
      default:
        throw new Error('Unsupported table format: ' + metadata.format);
    }

    return {
      data,
      labels,
      type: PlotType.TABLE,
    };
  }

  public static async buildTensorboardConfig(metadata: PlotMetadata): Promise<TensorboardViewerConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    WorkflowParser.parseStoragePath(metadata.source);
    return {
      type: PlotType.TENSORBOARD,
      url: metadata.source,
    };
  }

  public static async buildHtmlViewerConfig(metadata: PlotMetadata): Promise<HTMLViewerConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    const path = WorkflowParser.parseStoragePath(metadata.source);
    const htmlContent = await Apis.readFile(path);

    return {
      htmlContent,
      type: PlotType.WEB_APP,
    };
  }

  public static async buildMarkdownViewerConfig(metadata: PlotMetadata): Promise<MarkdownViewerConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    let markdownContent = '';
    if (metadata.storage === 'inline') {
      markdownContent = metadata.source;
    } else {
      const path = WorkflowParser.parseStoragePath(metadata.source);
      markdownContent = await Apis.readFile(path);
    }

    return {
      markdownContent,
      type: PlotType.MARKDOWN,
    };
  }

  public static async buildRocCurveConfig(metadata: PlotMetadata): Promise<ROCCurveConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    if (!metadata.schema) {
      throw new Error('Malformed metadata, property "schema" is required.');
    }
    if (!Array.isArray(metadata.schema)) {
      throw new Error('Malformed schema, must be an array of {"name": string, "type": string}');
    }

    const path = WorkflowParser.parseStoragePath(metadata.source);
    const stringData = csvParseRows((await Apis.readFile(path)).trim());

    const fprIndex = metadata.schema.findIndex(field => field.name === 'fpr');
    if (fprIndex === -1) {
      throw new Error('Malformed schema, expected to find a column named "fpr"');
    }
    const tprIndex = metadata.schema.findIndex(field => field.name === 'tpr');
    if (tprIndex === -1) {
      throw new Error('Malformed schema, expected to find a column named "tpr"');
    }
    const thresholdIndex = metadata.schema.findIndex(field => field.name.startsWith('threshold'));
    if (thresholdIndex === -1) {
      throw new Error('Malformed schema, expected to find a column named "threshold"');
    }

    const dataset = stringData.map(row => ({
      label: row[thresholdIndex].trim(),
      x: +row[fprIndex],
      y: +row[tprIndex],
    }));

    return {
      data: dataset,
      type: PlotType.ROC,
    };
  }

  public static async buildPythonVisualizationConfig(metadata: PlotMetadata, type: ApiVisualizationType): Promise<ViewerConfig> {
    if (!metadata.source) {
      throw new Error('Malformed metadata, property "source" is required.');
    }
    try {
      const visualization = await Apis.visualizationServiceApi.createVisualization({
        arguments: this.getPythonArgumentsForVisualizationType(metadata, type),
        source: metadata.source,
        type,
      });
      if (visualization.html) {
        return {
          htmlContent: visualization.html,
          type: PlotType.WEB_APP,
        } as HTMLViewerConfig;
      } else {
        throw new Error('Unable to generate visualization!');
      }
    } catch (err) {
      // Determine type and fall back to previous visualization method.
      // If no type can be determined, default to html.
      switch (type) {
        case ApiVisualizationType.ROCCURVE:
          return this.buildRocCurveConfig(metadata);
        case ApiVisualizationType.TABLE:
          return this.buildPagedTableConfig(metadata);
        default:
          return this.buildHtmlViewerConfig(metadata);
      }
    }
  }

  private static getPythonArgumentsForVisualizationType(metadata: PlotMetadata, type: ApiVisualizationType): string {
    switch (type) {
      case ApiVisualizationType.ROCCURVE:
        return JSON.stringify({
          'is_generated': 'True'
        });
      case ApiVisualizationType.TABLE:
        if (!metadata.header) {
          throw new Error('Malformed metadata, property "header" is required.');
        }
        return JSON.stringify({
          headers: metadata.header
        });
      default:
        return '{}';
    }
  }
}
