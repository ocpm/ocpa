# Import the OCEl import factory from the OCPA library. This factory is used to import event logs in the OCEl format.
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

# Define a test method to check if the process executions are correctly extracted from the event log.
def test_process_execution_extraction():
    # Path to the OCEl log file
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"

    # Use the OCEl import factory to import the log
    ocel = ocel_import_factory.apply(filename)

    # Assert that the number of process executions in the log is 80
    assert len(ocel.process_executions)== 80

# Define a test method to check if the process variants are correctly identified in the event log.
def test_variants():
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"
    ocel = ocel_import_factory.apply(filename)

    # Assert that the number of process variants in the log is 20
    assert len(ocel.variants)== 20

# Define a test method to check if process executions are correctly extracted by leading event type.
def test_process_execution_extraction__by_leading_type():
    filename = "sample_logs/jsonocel/p2p-normal.jsonocel"

    # Various parameters used for execution extraction and variant calculation
    parameters = {
        "execution_extraction": "leading_type",
        "leading_type": "GDSRCPT",
        "variant_calculation": "two_phase",
        "exact_variant_calculation": True
    }

    # Import log with the parameters
    ocel = ocel_import_factory.apply(filename, parameters=parameters)

    # Assert the number of process executions with leading type GDSRCPT is 80
    assert len(ocel.process_executions)== 80

    # Repeat the process for other leading event types - INVOICE, PURCHREQ, PURCHORD, and MATERIAL
    parameters = {"execution_extraction": "leading_type",
                  "leading_type": "INVOICE",
                  "variant_calculation": "two_phase",
                  "exact_variant_calculation": True}
    ocel = ocel_import_factory.apply(filename,parameters=parameters)
    assert len(ocel.process_executions) == 127

    parameters = {"execution_extraction": "leading_type",
                  "leading_type": "PURCHREQ",
                  "variant_calculation": "two_phase",
                  "exact_variant_calculation": True}
    ocel = ocel_import_factory.apply(filename,parameters=parameters)
    assert len(ocel.process_executions) == 80

    parameters = {"execution_extraction": "leading_type",
                  "leading_type": "PURCHORD",
                  "variant_calculation": "two_phase",
                  "exact_variant_calculation": True}
    ocel = ocel_import_factory.apply(filename,parameters=parameters)
    assert len(ocel.process_executions) == 80

    parameters = {"execution_extraction": "leading_type",
                  "leading_type": "MATERIAL",
                  "variant_calculation": "two_phase",
                  "exact_variant_calculation": True}
    ocel = ocel_import_factory.apply(filename, parameters=parameters)
    assert len(ocel.process_executions) == 414



