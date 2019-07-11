package main

import (
	"bytes"
	"fmt"
	"github.com/kubeflow/pipelines/bazel-ajchili-pipelines/external/go_sdk/src/io/ioutil"
	"os/exec"
	"path/filepath"
	"time"
)

func main() {
	visualizationPath, err := filepath.Abs("./backend/src/apiserver/visualizations/visualizer.py")
	if err != nil {
		panic(err)
	}
	visCommand := exec.Command("python3", visualizationPath)
	//buffer := bytes.Buffer{}
	outBuffer := bytes.Buffer{}
	//visCommand.Stdin = &buffer
	visCommand.Stdout = &outBuffer
	a, err := visCommand.StdinPipe()
	if err != nil {
		panic(err)
	}
	if err := visCommand.Start(); err != nil {
		panic(err)
	}
	args := "--predictions gs://kirinpatel/tfx-taxi-cab-classification-pipeline-example-s8726/predict/prediction_results-* --target_lambda \"lambda x: (x['target'] > x['fare'] * 0.2)\"\n"
	c := make(chan string)
	go func() {
		for outBuffer.Len() == 0 {
			time.Sleep(time.Second)
			//println("current buffer " + string(buffer.String()))
			println("waiting" + time.Now().String())
		}
		for outBuffer.Len() > 0 {
			_bytes, err := ioutil.ReadAll(&outBuffer)
			if err != nil {
				panic(err)
			}
			c <- string(_bytes)
		}
		close(c)
	}()
	go func() {
		println("sleep" + time.Now().String())
		time.Sleep(15 * time.Second)
		println("start" + time.Now().String())
		_, _ = a.Write([]byte(args))
	}()
	var html string
	for l := range c {
		html += l
	}
	fmt.Println(html)
	defer visCommand.Process.Kill()
}