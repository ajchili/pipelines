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

export enum PlotType {
  CONFUSION_MATRIX = 'confusion_matrix',
  MARKDOWN = 'markdown',
  ROC = 'roc',
  TABLE = 'table',
  TENSORBOARD = 'tensorboard',
  WEB_APP = 'web-app',
  PYTHON_VIS = 'python-vis'
}

// Interface to be extended by each viewer implementation, so it's possible to
// build an array of viewer configurations that forces them to declare their type.
export interface ViewerConfig {
  type: PlotType;
}

abstract class Viewer<P, S> extends React.Component<P, S> {
  public isAggregatable(): boolean {
    return false;
  }

  public abstract getDisplayName(): string;
}

export default Viewer;
