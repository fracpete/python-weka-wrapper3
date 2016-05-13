Flow
====

The flow components of *python-weka-wrapper3* are not related to Weka's KnowledgeFlow. Instead, they were
inspired by the `ADAMS workflow engine <https://adams.cms.waikato.ac.nz/>`_. It is a very simple workflow,
aimed at automating tasks and easy to extend as well. Instead of linking operators with explicit
connections, this flow uses a tree structure for implicitly defining how the data is processed.


Overview
--------

A workflow component is called an *actor*. All actors are derived from the `Actor` class,
but there are four different kinds of actors present:

* **source** actors generate data, but don't consume any
* **transformer** actors consume and generate data, similar to a filter
* **sink** actors only consume data, e.g., displaying data or writing to file
* **control** actors define how the data is passed around in a flow, e.g., branching

Data itself is being passed around in *Token* containers.

Due to the limitation of the tree structure of providing only 1-to-n connections, objects can be stored
internally in a flow using a simple dictionary (*internal storage*). Special actors store, retrieve,
update and delete these objects.

For finding out more about a specific actor, and what parameters it offers (via the `config` dictionary
property), you use one of the following actor methods:

* **print_help()** -- outputs a description of actor and its options on stdout
* **generate_help()** -- generates the help string output by `print_help()`

Printing the layout of a flow is very simple. Assuming you have a flow variable called `myflow`, you simply
use the `tree` method to output the structure: `print(myflow.tree)`

All actors can return and restore from JSON as well, simply use the following property to access or
set the JSON representation: `json`


Life cycle
----------

The typical life-cycle of a flow (actually any actor) can be described through the following method calls:

#. **setup()** configures and checks the flow (outputs error message if failed, None otherwise)
#. **execute()** performs the execution of actors (outputs error message if failed, None otherwise)
#. **wrapup()** finishes up the execution
#. **cleanup()** destructive, frees up memory


Sources
-------

The following *source* actors are available:

* **CombineStorage** expands storage items in a format string and forwards the generated string
* **DataGenerator** outputs artificial data
* **FileSupplier** outputs predefined file names
* **ForLoop** outputs integer tokens as defined by the loop setup (min, max, step)
* **GetStorageValue** outputs a storage from internal storage
* **ListFiles** lists files/directories
* **LoadDatabase** loads data from a database using an SQL query
* **Start** dummy source that just triggers the execution of other actors following
* **StringConstants** simply outputs a list of predefined strings, one by one


Transformers
------------

The following *transformers* are available:

* **AttributeSelection** performs attribute selection on a dataset and outputs an `AttributeSelectionContainer`
* **ClassSelector** sets/unsets the class attribute of a dataset
* **Convert** applies simple conversion schemes to the data passing through
* **Copy** creates a deep copy of serializable Java objects
* **CrossValidate** performs cross-validation on a classifier or clusterer
* **DeleteFile** deletes files that match a regular expression
* **DeleteStorageValue** deletes a value from internal storage
* **Evaluatie** evaluates a trained classifier/clusterer in internal storage on the data passing through
* **EvaluationSummary** generates a summary from a classifier/clusterer evaluation object
* **Filter** applies a Weka filter to the data passing through
* **InitStorageValue** sets the initial value for a internal storage value
* **LoadDataset** loads the data stored in the file received as input, either using automatic
  determined loader or user-specified one
* **MathExpression** computes a numeric value from a expression and numeric input
* **ModelReader** reads classifier/clusterer models from disk and forwards a `ModelContainer`
* **PassThrough** is a dummy that just passes through the tokens
* **Predict** applies classifier/clusterer model (serialized file or from storage) to incoming Instance objects
* **RenameRelation** updates the relation name of Instance/Instances objects
* **SetStorageValue** stores the payload of the current token in internal storage
* **Train** builds a classifier/clusterer/associator and passes on a `ModelContainer`
* **UpdateStorageValue** applies an expression to update an internal storage value, e.g.
  incrementing a counter


Sinks
-----

The following *sinks* are available:

* **ClassifierErrors** displays the classifier errors obtained from an Evaluation object
* **Console** just outputs a string representation of the object on stdout
* **DumpFile** similar to *Console*, but stores the string representation in a file
* **InstanceDumper** dumps incoming Instance/Instances object in a file
* **LinePlot** displays an Instances object as line plot, using the internal format
* **MatrixPlot** displays an Instances object as matrix plot
* **ModelWriter** stores a trained model on disk
* **Null** simply swallows any token (like `/dev/null` on Linux)
* **PRC** plots a precision-recall curve from an Evaluation object
* **ROC** plots a receiver-operator curver from an Evaluation object


Control actors
--------------

The following *control* actors define how data is getting passed around in a workflow:

* **Branch** forwards the same input token to all of its sub-branches
* **ContainerValuePicker** extracts a named value from a container, e.g. the `Model` from a `ModelContainer`
* **Flow** the outermost actor that also handles the internal storage
* **Sequence** executes its sub-actors sequentially, with the data generated by the previous being the input
  for the next one
* **Stop** stops the execution of the flow
* **Tee** allows to *tee* off the current token and process it separately in a sub-flow before continuing with
  the processing; optional condition available that determines when a token gets tee'd off
* **Trigger** executes its sub-actors whenever a token passes through (i.e., when the condition evaluates to True)


Conversions
-----------

The following *conversion* schemes can be used in conjunction with the *Convert* transformer:

* **AnyToCommandline** generates a command-line string from an object, e.g., a classifier
* **CommandlineToAny** generates an object from a command-line string, e.g., a classifier setup
* **PassThrough** is a dummy conversion that just passes through the data


Examples
--------

Check out the examples available through the *python-weka-wrapper3-examples* project on Github:

  https://github.com/fracpete/python-weka-wrapper3-examples

The example scripts are located in the `src/wekaexamples/flow` sub-directory.

Below is a code snippet for building a flow that cross-validates a classifier on a dataset
and outputs the evaluation summary and the ROC and PRC curves:

.. code-block:: python

    from weka.classifiers import Classifier
    from weka.flow.control import Flow, Branch, Sequence
    from weka.flow.source import FileSupplier
    from weka.flow.transformer import LoadDataset, ClassSelector, CrossValidate, EvaluationSummary
    from weka.flow.sink import Console, ClassifierErrors, ROC, PRC

    flow = Flow(name="cross-validate classifier")

    filesupplier = FileSupplier()
    filesupplier.config["files"] = ["/some/where/iris.arff"]
    flow.actors.append(filesupplier)

    loaddataset = LoadDataset()
    flow.actors.append(loaddataset)

    select = ClassSelector()
    select.config["index"] = "last"
    flow.actors.append(select)

    cv = CrossValidate()
    cv.config["setup"] = Classifier(classname="weka.classifiers.trees.J48")
    flow.actors.append(cv)

    branch = Branch()
    flow.actors.append(branch)

    seqsum = Sequence()
    seqsum.name = "summary"
    branch.actors.append(seqsum)

    summary = EvaluationSummary()
    summary.config["title"] = "=== J48/iris ==="
    summary.config["complexity"] = False
    summary.config["matrix"] = True
    seqsum.actors.append(summary)

    console = Console()
    seqsum.actors.append(console)

    seqerr = Sequence()
    seqerr.name = "errors"
    branch.actors.append(seqerr)

    errors = ClassifierErrors()
    errors.config["wait"] = False
    seqerr.actors.append(errors)

    seqroc = Sequence()
    seqroc.name = "roc"
    branch.actors.append(seqroc)

    roc = ROC()
    roc.config["wait"] = False
    roc.config["class_index"] = [0, 1, 2]
    seqroc.actors.append(roc)

    seqprc = Sequence()
    seqprc.name = "prc"
    branch.actors.append(seqprc)

    prc = PRC()
    prc.config["wait"] = True
    prc.config["class_index"] = [0, 1, 2]
    seqprc.actors.append(prc)

    # run the flow
    msg = flow.setup()
    if msg is None:
        msg = flow.execute()
        if msg is not None:
            print("Error executing flow:\n" + msg)
    else:
        print("Error setting up flow:\n" + msg)
    flow.wrapup()
    flow.cleanup()


With the following command you can output the built flow tree:

.. code-block:: python

    print(flow.tree)

The above example gets printed like this:

.. code-block:: none

    Flow 'cross-validate classifier'
    |-FileSupplier [files: 1]
    |-LoadDataset [incremental: False, custom: False, loader: weka.core.converters.ArffLoader]
    |-ClassSelector [index: last]
    |-CrossValidate [setup: weka.classifiers.trees.J48 -C 0.25 -M 2, folds: 10]
    |-Branch
    | |-Sequence 'summary'
    | | |-EvaluationSummary [title: === J48/iris ===, complexity: False, matrix: True]
    | | |-Console [prefix: '']
    | |-Sequence 'errors'
    | | |-ClassifierErrors [absolute: True, title: None, outfile: None, wait: False]
    | |-Sequence 'roc'
    | | |-ROC [classes: [0, 1, 2], title: None, outfile: None, wait: False]
    | |-Sequence 'prc'
    | | |-PRC [classes: [0, 1, 2], title: None, outfile: None, wait: True]


Extending
---------

Adding additional flow components is quite easy:

* Choose the superclass, based on how the actor is supposed to behave:

 * **source** -- `weka.flow.source.Source`
 * **transformer** -- `weka.flow.transformer.Transformer`
 * **sink** -- `weka.flow.sink.Sink`

* add the new class with a constructor like this `def __init__(self, name=None, options=None):`

* add a `description` method that returns a string, describing what your actor does

* added a `fix_config` method that ensures that all configurations are present and help for them as well
  (e.g., `transformer.ClassSelector`)

* if you want to output some additional info in the tree layout, implement a `quickinfo` method
  (see, e.g., `transformer.ClassSelector`)

* override the `setup` method if you require some additional checks (e.g., file actually exists)
  or setup steps (e.g., loading of model from disk); return None if everything OK, otherwise
  the error; don't forget to call the super-method.

* transformers or sink can check the input data by overriding the `check_input` method

* the actual execution or processing of input data happens in the `do_execute` method;
  return an error string if something failed, otherwise None; sources and transformers
  can append the generated data (wrapped in Token objects) to the `self._output` list
