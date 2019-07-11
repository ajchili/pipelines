package main

import (
	"io/ioutil"
	"net/http"
	"net/url"
)

func main() {
	resp, err := http.PostForm("http://localhost:8888", url.Values{"arguments": { "--predictions gs://kirinpatel/tfx-taxi-cab-classification-pipeline-example-s8726/predict/prediction_results-* --target_lambda \"lambda x: (x['target'] > x['fare'] * 0.2)\"" }})
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	println(string(body))
}