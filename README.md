# Nomoreguesswork

Motivated by empirical findings and guided by both developer intuition and previous software metrics, 
we conduct a static analysis of the source code to identify key features that influence tool selection. 
This analysis leads us to organize 60 key features into four categories—code complexity, semantic attributes, program scale, and usage scenario, each capturing a distinct aspect of what makes code under test more suitable for one approach over the other. 
After that, we train a simple classifier named TestGenSelector based on these features that predicts which tool is better suited for the code under test. 
Compared to using deep learning models based on Transformer architectures, our classifier is simple and offers interpretable features. 
TestGenSelector achieves around 80\% classification precision and improves UTG coverage by 5\%--18\% compared to baseline methods. 
This work provides actionable guidance for practitioners and lays the groundwork for intelligent test generation systems. 
Complete feature descriptions can be found in the [All feature.pdf](analysis/All feature.pdf) file in the current project directory.

<img src="analysis/pipe.png" />
By quantifying coverage differences per project, we assess whether tool performance depends on code features, thereby motivating the need for tool-specific selection strategies. 
The empirical study pipeline is shown in the green box of Figure. 
We construct the data collection and then generate the test cases for two types of tools respectively .


