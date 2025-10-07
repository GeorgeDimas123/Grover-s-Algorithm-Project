from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister # imports necessary qskit libraries
from qiskit.visualization import plot_histogram # imports basic plot tools
from qiskit_ibm_runtime import QiskitRuntimeService # imports necessary qskit libraries to connect to backends
from qiskit_aer import AerSimulator # imports the simulation 
from qiskit_ibm_runtime import Sampler # imports sampler
from qiskit import transpile # imports the package to transpile the circuit
from qiskit_ibm_runtime import QiskitRuntimeService # imports package to connect to real-world backends
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Function("initialization"): creates initial state for grover algorithm
# ================================
def initialization(quantumCircuit):
    n = quantumCircuit.num_qubits # gets total number of qubits from given circuit

    # adds a H gate to all input qubits for intialization
    for qubit in range(n-1):
        quantumCircuit.h(qubit)

    quantumCircuit.x(n-1) # applies NOT gate to ancilla qubit
    quantumCircuit.h(n-1) # apples H gate to ancilla qubit (making a superpostion)
    quantumCircuit.barrier()

    return quantumCircuit
# ================================

n = 2 # intializes total number of qubits
qr = QuantumRegister(n, "q") # creates quantum register called q
anc = QuantumRegister(1, "ancillary") # creates a single ancillary qubit
meas = ClassicalRegister(3, "meas")
initialization_circuit = QuantumCircuit(qr, anc) # constructs a quantum circuit with 2 qubits and 1 ancillary
 
initialization(initialization_circuit) # calls "initialization" function to create input for the algorithm
initialization_circuit.draw() # draws circuit (input state)

# Function("oracle"): marks the target spot by applying phase shift
# ================================
def oracle(quantumCircuit):
    quantumCircuit.x(1) # adds X gate to q1
    quantumCircuit.ccx(0, 1, 2) # applies toffoli gate to all qubits
    quantumCircuit.x(1) # adds a second X gate to q1
    quantumCircuit.barrier()
# ================================

oracle_circuit = QuantumCircuit(qr, anc)
oracle(oracle_circuit)
oracle_circuit.draw() # draws circuit (all gates used in oracle)

# Function("diffusionOperator"): increases amplitude of marked state
# ================================
def diffusionOperator(quantumCircuit):
    inputQubits = quantumCircuit.num_qubits - 1
    quantumCircuit.h(range(0, inputQubits))
    quantumCircuit.x(range(0, inputQubits))
    quantumCircuit.h(inputQubits-1)
    quantumCircuit.mcx([i for i in range(0, inputQubits - 1)], inputQubits - 1)
    quantumCircuit.h(inputQubits-1)
    quantumCircuit.x(range(0, inputQubits))
    quantumCircuit.h(range(0, inputQubits))
    quantumCircuit.barrier()
# ================================

diffusion_circuit = QuantumCircuit(qr, anc)
diffusionOperator(diffusion_circuit)
diffusion_circuit.draw()

# 2-bit grover search
# ================================
n = 2
qr = QuantumRegister(n, "q")
anc = QuantumRegister(1, "ancillary")
meas = ClassicalRegister(3, "meas")
grover_circuit = QuantumCircuit(qr, anc, meas)
numIterations = 1
initialization(grover_circuit)

for i in range(0, numIterations):
    oracle(grover_circuit)
    diffusionOperator(grover_circuit)

# clear the ancilla bit
grover_circuit.h(n)
grover_circuit.x(n)
grover_circuit.measure_all(add_bits=False)

grover_circuit.draw()
# ================================

# Printing results using simulator
# ================================
# Define backend
backend = AerSimulator()
 
# Transpile to backend
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_qc = pm.run(grover_circuit)
 
# Run the job
sampler = Sampler(mode=backend)
job = sampler.run([isa_qc])
result = job.result()

# Print the results
counts = result[0].data.meas.get_counts()
print(counts)
 
# Plot the counts in a histogram
plot_histogram(counts)
# ================================

# Printing results using real IBM quantum computer
# ================================
service = QiskitRuntimeService(channel="ibm_quantum_platform", token="ENTER YOUR TOKEN HERE")
real_backend = service.backend("ibm_kingston")

transpiled_circuit = transpile(grover_circuit, backend=real_backend, optimization_level=1)
transpiled_circuit.draw()

sampler = Sampler(real_backend)
real_job = sampler.run([transpiled_circuit])
real_results = real_job.result()

print(real_results[0].data.meas.get_counts())
plot_histogram(real_results[0].data.meas.get_counts())
# ================================