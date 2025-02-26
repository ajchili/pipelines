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

import * as React from 'react';
import ConfusionMatrix from './ConfusionMatrix';
import HTMLViewer from './HTMLViewer';
import MarkdownViewer from './MarkdownViewer';
import PagedTable from './PagedTable';
import ROCCurve from './ROCCurve';
import TensorboardViewer from './Tensorboard';
import PythonVisViewer from './PythonVisViewer';
import { PlotType, ViewerConfig } from './Viewer';

export const componentMap = {
  [PlotType.CONFUSION_MATRIX]: ConfusionMatrix,
  [PlotType.MARKDOWN]: MarkdownViewer,
  [PlotType.ROC]: ROCCurve,
  [PlotType.TABLE]: PagedTable,
  [PlotType.TENSORBOARD]: TensorboardViewer,
  [PlotType.WEB_APP]: HTMLViewer,
  [PlotType.PYTHON_VIS]: PythonVisViewer,
};

interface ViewerContainerProps {
  configs: ViewerConfig[];
  maxDimension?: number;
}

class ViewerContainer extends React.Component<ViewerContainerProps> {
  public render(): JSX.Element | null {
    const { configs, maxDimension } = this.props;
    if (!configs.length) {
      return null;
    }

    // tslint:disable-next-line:variable-name
    const Component = componentMap[configs[0].type];
    return <Component configs={configs as any} maxDimension={maxDimension} />;
  }
}

export default ViewerContainer;
