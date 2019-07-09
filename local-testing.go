package main

import (
	"bytes"
	"fmt"
	"os/exec"
)

func main() {
	visCommand := exec.Command("python3", "/usr/local/google/home/kirinpatel/Documents/ajchili-pipelines/backend/src/apiserver/visualizations/visualizer.py")
	buffer := bytes.Buffer{}
	outBuffer := bytes.Buffer{}
	visCommand.Stdin = &buffer
	visCommand.Stdout = &outBuffer
	if err := visCommand.Start(); err != nil {
		panic(err)
	}
	args := "--predictions gs://kirinpatel/tfx-taxi-cab-classification-pipeline-example-s8726/predict/prediction_results-* --target_lambda \"lambda x: (x['target'] > x['fare'] * 0.2)\"\n"
	buffer.Write([]byte(args))
	var html string
	for outBuffer.Len() == 0 {}
	for outBuffer.Len() > 0 {
		_bytes, err := outBuffer.ReadByte()
		if err != nil {
			panic(err)
		}
		html += string(_bytes)
	}
	fmt.Println(html)
}