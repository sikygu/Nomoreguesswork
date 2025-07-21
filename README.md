# Nomoreguesswork

Motivated by empirical findings and guided by both developer intuition and previous software metrics, 
we conduct a static analysis of the source code to identify key features that influence tool selection. 
This analysis leads us to organize 60 key features into four categories—code complexity, semantic attributes, program scale, and usage scenario, each capturing a distinct aspect of what makes code under test more suitable for one approach over the other. 
After that, we train a simple classifier named TestGenSelector based on these features that predicts which tool is better suited for the code under test. 
Compared to using deep learning models based on Transformer architectures, our classifier is simple and offers interpretable features. 
TestGenSelector achieves around 80\% classification precision and improves UTG coverage by 5\%--18\% compared to baseline methods. 
This work provides actionable guidance for practitioners and lays the groundwork for intelligent test generation systems. 
Complete feature descriptions can be found in the[All feature.pdf](analysis/All-feature.pdf) file in the current project directory.

<img src="analysis/pipe.png" />

By quantifying coverage differences per project, we assess whether tool performance depends on code features, thereby motivating the need for tool-specific selection strategies. 
The empirical study pipeline is shown in the green box of Figure. 
We construct the data collection and then generate the test cases for two types of tools respectively .


The following is a brief description of some features:
## Code Complexity Metrics
This section outlines key metrics used to evaluate code complexity, focusing on logical complexity, coupling, and theoretical complexity.

### Logical Complexity Metrics

#### Maximum Cyclomatic Complexity (OCmax)
OCmax measures the highest cyclomatic complexity among all non-abstract methods in a class. Each method starts with a base complexity of 1, increasing by 1 for each control flow structure (e.g., for loops, if statements, while loops, ternary operators, or switch case statements, excluding consecutive cases). This metric indicates the number of branches in the code, reflecting how difficult a method is to understand.

#### Average Operation Complexity (OCavg)
OCavg is the average cyclomatic complexity across all non-abstract methods in a class. It provides an average measure of logical complexity for a class's methods.

#### Weighted Methods per Class (WMC)
WMC is the sum of cyclomatic complexities of all methods in a class, calculated as:


$$\text{WMC} = \sum (\text{cyclomatic complexity of each method})$$


This metric captures the total logical complexity of a class’s method set.


#### Number of Dependencies (Dcy)
Dcy counts the number of other classes a given class depends on, calculated using a dependency graph and graph traversal algorithms. High dependency counts indicate lower modularity.

#### Number of Transitive Dependencies (Dcy*)
Dcy* extends Dcy by including both direct and indirect dependencies, reflecting a class’s deeper coupling within the dependency network.

#### Number of Dependents (DPT)
DPT measures the number of classes that directly depend on the current class, identified by searching for references to the class within the project.

#### Number of Transitive Dependents (DPT*)
DPT* counts classes that indirectly depend on the current class through dependency chains, calculated using graph traversal algorithms to identify transitive dependencies.

#### Cyclic Dependencies (Cyclic)
Cyclic counts the number of classes involved in cyclic dependencies (direct or indirect) with the current class. It is calculated by constructing a dependency graph, identifying strongly connected components, and counting them (subtracting 1 for the class itself).

### Theoretical Complexity Metrics

#### Level (Level)
Level measures the number of dependency "layers" for a class. A class with no dependencies has a Level of 0. For classes with dependencies, it is calculated as:


$$\text{Level} = \max(\text{Level of dependent classes}) + 1$$


This excludes classes with mutual or cyclic dependencies.

#### Adjusted Level (Level*)
Level* builds on Level by accounting for cyclic dependencies. It is calculated as:

$$
\text{Level*} = \max(\text{Level* of non-cyclic dependencies}) + \text{number of cyclic dependencies}
$$


#### Depth of Inheritance Tree (DIT)
DIT measures the depth of a class’s inheritance hierarchy, counting the levels from the class to the root (e.g., java.lang.Object). Each parent class increments the depth by 1. Deep inheritance trees can increase design complexity.



## Semantic Attributes

These metrics focus on comments and documentation to assess code readability and quality.

#### Comment Lines of Code (CLOC)
CLOC counts the total number of lines containing comments in a code file:

$$
\text{CLOC} = \left| \{ l \in L \mid l \text{ contains comment content} \} \right|
$$

where \( L \) is the set of non-blank code lines. It reflects comment density and code interpretability.

#### Comment Ratio (COM_RAT)
COM_RAT is the ratio of comment lines to total non-blank code lines:

$$
\text{COM_RAT} = \frac{\text{CLOC}}{|L|}
$$

This measures the relative density of comments, indicating code readability.

#### Javadoc Method Coverage (JM)
JM measures the percentage of methods with Javadoc comments:

$$
\text{JM} = \frac{|\text{methods with Javadoc comments}|}{|\text{total methods in the class}|} \times 100\%
$$

#### Javadoc Field Coverage (JF)
JF measures the percentage of fields with Javadoc comments:

$$
\text{JF} = \frac{|\text{fields with Javadoc comments}|}{|\text{total fields in the class}|} \times 100\%
$$


## Program Scale Metrics

These metrics quantify the physical and logical size of code.

#### Lines of Code (LOC)
LOC counts the total number of code lines in a class, including comments but excluding blank lines.

#### Non-Comment Lines of Code (NCLOC)
NCLOC is LOC minus pure comment lines:

$$
\text{NCLOC} = \text{LOC} - \left| \{ l \in L \mid l \text{ is a pure comment line} \} \right|
$$

This reflects the scale of executable code.

#### Class Size Attributes (CSA)
CSA counts non-static attributes in a class:

$$
\text{CSA} = \left| \{ f \in F \mid f \text{ is a non-static field defined in the class} \} \right|
$$

#### Class Size Operations (CSO)
CSO counts non-static methods in a class:

$$
\text{CSO} = \left| \{ m \in M \mid m \text{ is a non-static method defined in the class} \} \right|
$$

#### Class Size (Operations + Attributes) (CSOA)
CSOA is the sum of CSA and CSO, measuring the logical scale of a class.

#### Maximum Operation Size (OSmax)
OSmax is the number of statements in the largest method in a class:

$$
\text{OSmax} = \max( \{ \text{number of statements in method } m \mid m \in M \} )
$$

#### Number of Operations Overridden (NOOC)
NOOC counts methods in a subclass that override parent class methods.

#### Number of Operations Inherited (NOIC)
NOIC counts methods inherited by a class, excluding constructors, private, static, abstract, or locally defined methods.

## Usage Scenarios

These scenarios describe common code functionalities and responsibilities based on developer intuition and empirical studies.

#### String Processing
Involves creating, manipulating, parsing, formatting, or converting strings, such as text processing, report generation, input sanitization, string splitting, concatenation, or regular expression matching.

#### File Operations
Covers interactions with the file system, including file creation, reading, and path management (e.g., reading configuration files or exporting data to CSV).

#### Database Operations
Handles database connections, queries, updates, or transaction management, such as executing SQL queries, using ORMs, or defining data models.

#### Mathematical Computation
Focuses on numerical computations, algorithm implementations, or statistical analyses, including financial calculations, machine learning predictions, or geometric operations.
