# Nomoreguesswork

By quantifying coverage differences per project, we assess whether tool performance depends on code features, thereby motivating the need for tool-specific selection strategies. 
The empirical study pipeline is shown in the green box of Figure. 
We construct the data collection and then generate the test cases for two types of tools respectively .
<img height="450" src="C:\Users\17958\Desktop\main.pdf" title="Overview of the research pipeline" width="600"/>

# Description of the Full Set of 60 Static Code Features

### Section 1: Code Complexity
These features primarily encompass logical complexity (cyclomatic complexity, cohesion), coupling (dependency relationships, inheritance depth), and theoretical complexity. 

**Maximum Cyclomatic Complexity (OCmax)**: This is a logical complexity metric defined in [ocmax], which is the maximum cyclomatic complexity among all non-abstract methods within a class. The base complexity of each method is 1, and the complexity increases by 1 for each occurrence of the following control flow structures: for loops, foreach loops, if statements, do-while loops, conditional expressions (ternary operators), while loops, and each case in a switch statement (excluding consecutive cases). This metric reflects the number of branches in the code and is closely related to the difficulty of understanding a method. 

**Average Operation Complexity (OCavg)**: We define OCavg as the average cyclomatic complexity of all non-abstract methods in a class, which is derived from the OCmax feature [ocmax]. This metric reflects the logical complexity of the set of methods in a class on an average basis. 

**Weighted Methods per Class (WMC)**: This is a logical complexity metric defined in [ck-metric], which is the sum of the complexities of all methods in a class. It is calculated as: 
\[
\text{WMC} = \sum (\text{cyclomatic complexity of each method})
\]
This metric comprehensively reflects the total logical complexity of all methods in a class and is closely related to the overall logical complexity of the method set of the class. 

**Number of Dependencies (Dcy)**: This is an object-oriented coupling metric defined in [DBLP], which is the number of other classes that a class depends on. This feature is calculated by constructing a dependency graph combined with graph traversal algorithms and is negatively correlated with the modularity of the system. 

**Number of Transitive Dependencies (Dcy*)**: The number of other classes that a class depends on either directly or indirectly, which is derived from the Dcy feature [DBLP]. The difference from Dcy is that it includes both the number of directly dependent classes and the number of indirectly dependent classes. This feature can reflect the deep coupling state of a class in the dependency network. 

**Number of Dependents (DPT)**: This is an object-oriented coupling metric defined in [DBLP], which is the number of other classes that directly depend on the current class. We first search for other classes in the project that use the current class, and then count the number of classes that reference the current class as a result. 

**Number of Transitive Dependents (DPT*)**: This is an object-oriented coupling feature defined in [DBLP], which is the number of classes that indirectly depend on the current class through a dependency chain. We construct a dependency graph and use graph traversal algorithms to find all transitive dependencies, then count the number of classes that indirectly depend on the current class. 

**Cyclic Dependencies (Cyclic)**: This is an object-oriented coupling feature defined in [Cyclic], which is the number of classes that each class depends on either directly or indirectly, and these dependencies also depend back on the class either directly or indirectly. It represents the number of other classes involved in cyclic dependencies. For the calculation of this feature, we first construct a dependency graph and collect all direct dependencies. Then we calculate the transitive dependency relationships and identify strongly connected components. Finally, we count the strongly connected components and subtract 1. 

**Level (Level)**: This is an object-oriented theoretical complexity feature defined in [level/*], which measures how many "layers" of classes a class depends on. For a class that does not depend on other classes in the project, its value is 0; for a class with dependencies, its value is equal to the maximum Level value among the classes it depends on plus 1, excluding classes with mutual dependencies or cyclic dependencies. That is: 
\[
\text{level} = \max(\text{level of dependent classes}) + 1
\]

**Adjusted Level (Level*)**: This is an object-oriented theoretical complexity feature defined in [level/*], which considers the number of classes in cyclic dependencies on the basis of measuring how many "layers" of classes a class depends on. Its calculation method is similar to Level: for a class that does not depend on other classes in the project, its value is 0; for a class with dependencies, its value is equal to the maximum Level* value among the classes it depends on, plus the number of classes that have mutual dependencies or form cyclic dependencies with it. That is: 
\begin{align*}
\text{level} &= \max(\text{Level* of non-cyclic dependencies}) \\
&+ \text{number of cyclic dependencies}
\end{align*}

**Package Dependency Count (PDcy)**: Derived from Robert C. Martin's package-level dependency metric "Efferent Couplings (Ce)" [pdcy], we extend it to the class level. This metric is defined as the number of external packages that a class directly depends on, reflecting the coupling degree between the class and external modules. 

**Transitive Package Dependency Count (PDcy*)**: Considering the problem of cyclic dependencies, this feature is introduced on the basis of PDcy [pdcy]. It represents the number of packages that a class directly and indirectly depends on, and this feature is closely related to code structure and modularity. 

**Package Dependents (PDpt)**: PDpt is a dependency feature corresponding to PDcy [pdcy], defined as the number of packages that directly or indirectly depend on the current class. It is obtained by counting the number of packages that directly or indirectly depend on the class. 

**Depth of Inheritance Tree (DIT)**: This is an object-oriented inheritance depth metric defined in [ck-metric], which is the depth of the inheritance tree of each class. DIT is calculated recursively by tracing the inheritance chain of a class from the current class to the root class (java.lang.Object). The depth value increases by 1 for each level up to the parent class. If there is no parent class (i.e., the top of the inheritance chain is reached), 0 is returned. This metric is closely related to the complexity of software design, as an excessively deep inheritance tree makes the code difficult to understand and maintain. 

**Coupling Between Objects (CBO)**: This is an object-oriented coupling metric defined in [ck-metric], which measures the degree of "coupling" between a class and other classes. Specifically, two classes are coupled when one class depends on the other or is dependent on the other. Its calculation method is as follows: 
\begin{align*}
\text{CBO} &= \bigl| \text{Set of classes dependent on the current class} \\
&\cup \text{Set of classes the current class depends on} \bigr|
\end{align*}

**Message Passing Coupling (MPC)**: Briand proposed a quantification method for message passing coupling, defining MPC as "the number of statements in a class that call methods of other classes" [mpc]. Based on this definition, we adjust it to: the number of messages (method calls) sent by a class to other classes, excluding calls to methods of the same class. This metric measures the inter-class coupling degree from the perspective of the frequency of dynamic interactions between classes. 

**Lack of Cohesion of Methods (LCOM)**: This is an object-oriented cohesion feature defined in [ck-metric], which measures the degree of lack of cohesion between methods of a class. We use the LCOM variant designed by Hitz and Montazeri for calculation. First, a relationship graph between methods is constructed, where nodes are methods and edges represent relationships between methods. Then, the number of connected components in this relationship graph is calculated as the result. This feature is closely related to the cohesion and responsibilities of the class. 

**Response for Class (RFC)**: Represents the size of the response set of a class, including methods in the class and called external methods [ck-metric]. It is obtained by counting all methods defined in the class and all external methods called, and a higher value indicates more complex behaviour of the class. 

**Number of Queries (Query)**: The Query metric quantifies the ability of a class to provide information query services, expressed as the number of non-constructor methods with return values in the class (excluding inherited methods) [query]. The formal definition is: 

\begin{align*}
\text{Query} &= \left| \bigl\{ m \in M \mid m \text{ is a non-constructor method} \right. \\
&\left. \quad \text{with a return type} \neq \text{void} \bigr\} \right|
\end{align*}

where M is the set of methods defined in the class. This feature can measure the strength of the information query ability provided by the class and is closely related to the design complexity and responsibility allocation of the code.

**Halstead's Bug Prediction ($B$)**
\[
B = \frac{V}{\ln(2)} \times \frac{D}{3000}
\]
where $V$ is the Halstead Volume and $D$ is the Halstead Difficulty. This metric estimates the number of latent bugs in a program [halstead].

**Halstead Length ($N$)**
The total number of operator and operand occurrences [halstead] in a program:
\[
N = N_1 + N_2
\]
- $N_1$: Total number of operator occurrences
- $N_2$: Total number of operand occurrences

**Halstead Vocabulary ($n$)**
The total number of distinct operators and operands [halstead]:
\[
n = n_1 + n_2
\]
- $n_1$: Number of distinct operators
- $n_2$: Number of distinct operands

**Halstead Difficulty ($D$)**
A measure of program complexity based on operator and operand diversity [halstead]:
\[
D = \frac{n_1}{2} \times \frac{N_2}{n_2}
\]

**Halstead Volume ($V$)**
The information content required to implement the program [halstead]:
\[
V = N \times \log_2(n)
\]

**Halstead Effort ($E$)**
The mental effort required to develop or understand the program [halstead]:
\[
E = D \times V
\]

### Section 2: Semantic Attributes
These features primarily focus on comments and documentation information within code to assess its readability and documentation quality. 

**Comment Lines of Code (CLOC)**: This feature is an extension of the concept of Source Lines of Code (SLOC) proposed by Nguyen, defined as the total number of lines in a code file that contain comment content [sloc]. Its calculation rules adhere to strict syntactic parsing, with a formal representation as:
\begin{equation}
\text{CLOC} = \left| \{ l \in L \mid l \text{ contains comment content} \} \right|
\end{equation}
where \( L \) is the set of code lines after excluding blank lines. CLOC reflects the physical density of comments in the code and is closely related to the code's interpretability.

**Comment Ratio (COM_RAT)**: This is a feature for code comments defined in [2013comparative], representing the ratio of the number of comment lines to the total number of code lines (excluding blank lines) in the code. This feature reflects the relative density of comments in the code and is a classic feature for assessing code readability. Its formal representation is:
\begin{equation}
\text{COM_RAT} = \frac{\text{CLOC}}{|L|}
\end{equation}
where \( |L| \) denotes the cardinality of the set \( L \) of non-blank code lines.

**Javadoc Method Coverage (JM)**: JM is closely related to the completeness of method-level documentation. JM is defined as:
\begin{equation}
\text{JM} = \frac{|\text{methods with Javadoc comments}|}{|\text{total methods in the class}|} \times 100\%.
\end{equation}

**Javadoc Field Coverage (JF)**: This is a feature for code comments defined in [javadoc], quantifies the documentation level of fields within a class. It is defined as:
\begin{equation}
\text{JF} = \frac{|\text{fields with Javadoc comments}|}{|\text{total fields in the class}|} \times 100\%.
\end{equation}

**Javadoc Lines of Code (JLOC)**: JLOC is a refined metric of CLOC, specifically counting the number of lines of comments that conform to the Javadoc specification [javadoc]. This metric measures the density of comments in the code that follow standard API documentation conventions and is strongly associated with the completeness of API documentation. Its calculation is:
\begin{equation}
\text{JLOC} = \left| \{ l \in L \mid l \text{ belongs to a Javadoc comment block} \} \right|
\end{equation}

**True Comment Ratio (TCOM_RAT)**: Defined as the ratio of the number of true comment lines to the total number of code lines (excluding blank lines). Here, true comment lines refer to those that exclude automatically generated comments (e.g., auto-generated TODO comments) and only include meaningful documentation comments or explanatory comments. This metric reflects the quality density of effective comments in the code and can be used to assess code readability and documentation completeness.

**Number of TODO Comments (TODO)**: This refers to the total number of TODO comments within a class [storey2008todo].

### Section 3: Program Scale
These features are primarily used to quantify the physical size of code (e.g., lines of code, number of methods/attributes) and the scale of logical structures (e.g., parameters, inner classes).

**Lines of Code (LOC)**: This is a metric defined in [2013comparative], which is the total number of lines of code in a class. As a fundamental indicator for measuring code size, it includes comment lines but excludes pure blank lines (lines containing only spaces, tabs, etc., are not counted).

**Non-Comment Lines of Code (NCLOC)**: NCLOC is a derivative indicator of LOC [2013comparative], defined as:
\[
\text{NCLOC} = \text{LOC} - \left| \{ l \in L \mid l \text{ is a pure comment line} \} \right|
\]
By eliminating the interference of comments, this indicator accurately reflects the scale of actual executable code.

**Class Size Attributes (CSA)**: CSA is defined as the number of non-static attributes defined in a class [2013comparative]. Its formal representation is:
\begin{align*}
\text{CSA} &= \left| \bigl\{ f \in F \mid f \text{ is a non-static field} \right. \\
&\left. \quad \text{defined in the current class} \bigr\} \right|
\end{align*}
where \( F \) is the set of all fields in the class.

**Class Size Operations (CSO)**: As a dual indicator of CSA, CSO is defined as the number of non-static methods defined in a class [2013comparative]. Its formal representation is:
\begin{align*}
\text{CSO} &= \left| \bigl\{ m \in M \mid m \text{ is a non-static method} \right. \\
&\left. \quad \text{defined in the current class} \bigr\} \right|
\end{align*}
where \( M \) is the set of all methods in the class.

**Class Size (Operations + Attributes) (CSOA)**: This is a metric for measuring the logical scale of a class, which is the total number of operations and attributes in the class, i.e., the sum of CSA and CSO.

**Maximum Operation Size (OSmax)**: This is a metric for measuring the structural scale of a class defined in [osmax], referring to the number of statements in the largest method within the class. Its formal representation is:
\[
\text{OSmax} = \max( \{ \text{number of statements in method } m \mid m \in M \} )
\]

**Average Operation Size (OSavg)**: This is a derivative indicator of OPavg [opavg], defined as the average number of statements per method in the class. It is calculated as:
\[
\text{OSavg} = \frac{ \sum_{m \in M} \text{(number of statements in method } m) }{ |M| }
\]

**Average Number of Parameters (OPavg)**: This is a metric for measuring the structural scale of a class defined in [opavg], referring to the average number of parameters per method in the class. Here, we use OPavg instead of NPAVG in the citation, and this indicator is closely related to the complexity of method interfaces. It is calculated as:
\[
\text{OPavg} = \frac{ \sum_{m \in M} \text{(number of parameters in method } m) }{ |M| }
\]

**Number of Operations Added (NOAC)**: This is a metric for measuring the structural scale of a class defined in [opavg], referring to the number of new methods added by a subclass. Its formal representation is:
\begin{align*}
\text{NOAC} &= \left| \bigl\{ m \in M_{\text{sub}} \mid m \notin M_{\text{super}} \right. \\
&\left. \quad \text{and } m \text{ is not an overridden method} \bigr\} \right|
\end{align*}
where \( M_{\text{sub}} \) is the set of methods in the subclass, and \( M_{\text{super}} \) is the set of methods in the parent class. Here, we use NOAC instead of NMA in the citation; this indicator only counts newly defined methods in the class, excluding methods inherited from the parent class and overridden methods.

**Number of Attributes Added (NAAC)**: As a dual indicator of NOAC [opavg], NAAC is defined as the number of new attributes added in the class. Specifically, this indicator first counts the attributes directly defined in the class, then excludes attributes inherited from the parent class, and finally calculates the number of newly added fields in the current class as the result.

**Number of Operations Overridden (NOOC)**: This is a metric for measuring the logical scale of a class, referring to the number of methods in a subclass that override methods in the parent class. Here, we use NOOC instead of NMO in [opavg]; this indicator first checks each method in the class, then determines whether it uses the @Override annotation or overrides a parent class method, and finally counts the number of overridden methods as the result.

**Number of Operations Inherited (NOIC)**: This is a derivative indicator of NOAC [opavg], defined as the total number of operations (or methods) inherited by a class. Specifically, it first traverses all methods of the class, then excludes constructors, private methods, static methods, abstract methods, and methods defined by the current class itself; the remaining number of methods is the value of NOIC.

**Number of Children (NOC)**: This is an object-oriented metric for measuring the structural scale of a class defined in [ck-metric], referring to the total number of direct subclasses of a class. This indicator can also help evaluate the inheritance hierarchy and reuse of classes. A high NOC value indicates that the class is widely inherited, suggesting it may be a well-designed base class/superclass.

**Number of Constructors (CONS)**: Represents the total number of constructors declared in a class [osmax]. This metric only counts explicitly declared constructors in the class; if no constructors are declared (even if a default constructor exists), the value of the indicator is 0.

**Number of Implemented Interfaces (INNER)**: Considering the need to characterize the scale of a class from the perspective of interface implementation, we define this indicator as the total number of interfaces implemented by the class [INNER]. Specifically, this feature counts all distinct interfaces implemented directly or indirectly by a class, including interfaces implemented directly and interface implementations inherited from parent classes.

**Number of Inner Classes (Inner)**: This is a derivative indicator of NOAC [opavg], defined as the number of inner classes or interfaces contained in a class.

**Number of Type Parameters (NTP)**: This is a metric for measuring the structural scale of a class defined in [ntp], referring to the number of type parameters in the class. A high NTP value indicates that the class uses more type parameters, which may lead to an increase in class scale.

**Number of Statements (STAT)**: Defined as the number of valid statements in a method. It first traverses all PSI statement nodes, then excludes empty statements and block statements, and finally counts the actual executable statements as the result.

### Section 4: Usage Scene
Drawing upon developers' intuition and empirical studies, we have identified 10 typical code scenarios, with a primary focus on code functionality and responsibilities. 

**String Processing**: This scenario encompasses the creation, manipulation, parsing, formatting, or conversion of strings [testwar]. Examples include processing text data, generating reports, sanitising inputs, and methods such as string splitting, concatenation, and regular expression matching. 

**File Operations**: This scenario involves interactions with the file system and manipulation of file contents, specifically including file creation, reading, and the parsing and management of file paths. Examples include reading configuration files and exporting data to CSV. 

**Database Operations**: This scenario primarily handles database connections, queries, updates, or transaction management. Examples include executing SQL queries, manipulating ORMs (Object-Relational Mappers), managing data storage, or defining data models. 

**Mathematical Computation**: This scenario primarily performs numerical computations, algorithm implementations, or statistical analyses, encompassing mathematical functions, statistical models, or optimisation algorithms. Examples include handling financial calculations, machine learning predictions, or geometric operations. 

**User Interface**: This scenario manages user interactions, interface rendering, or event handling. Examples include building web frontends, desktop GUIs, or mobile interfaces. 

**Business Logic**: This scenario primarily implements specific business rules or domain logic, which are specific to the application context. Examples include user permission validation, workflow engines, etc. 

**Data Structures and Algorithms**: This scenario manages data collections and implements efficient storage or manipulation. Examples include handling lists, trees, graphs, traversing data structures, or optimising methods (e.g., sorting, searching). 

**System and Tools**: This scenario primarily provides general auxiliary functionalities or system-level operations, such as logging, error handling, or process management. Other categories typically reuse code in this category. 

**Concurrency and Multithreading**: This scenario primarily deals with parallel execution, thread management, or resource sharing. Examples include implementing asynchronous tasks or avoiding race conditions. 

**Exception Handling**: This scenario is responsible for uniformly managing the system's exception handling mechanisms, including the capture, classification, handling, and reporting of exceptions, as well as the implementation of exception recovery strategies, etc.

