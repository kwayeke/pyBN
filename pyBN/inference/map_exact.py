"""
************************************
Exact Maximum A Posteriori Inference
************************************

Perform exact MAP inference over a BayesNet object,
with or without evidence.

Eventually, there will be a wrapper function "map_exact"
for all of the algorithms, and users can choose their method as
an argument to that function.

Exact MAP Inference Algorithms
------------------------------

	- Max-Sum Variable Elimination


References
----------
[1] Koller, Friedman (2009). "Probabilistic Graphical Models."

"""

__author__ = """N. Cullen <ncullen.th@dartmouth.edu>"""


def map_var_elim(bn,
				target=None,
				evidence=None, 
				order=None):
	"""
	Perform Max-Sum Variable Elimination over a BayesNet object
	for exact maximum a posteriori inference.

	Parameters
	----------


	Returns
	-------


	Effects
	-------


	Notes
	-----
	Clearly, "self" references need to be cleaned up.
	Initialization of "self" from old code:
	
	self.BN = BN
    if v_list:
        self.f_list = [Factor(BN,var) for var in v_list if var in self.BN.V]
        self.v_list = v_list
    else:
        self.f_list = [Factor(BN,var) for var in self.BN.V]
        self.v_list = BN.V
    self.temp_f_list = None # used so we can run multiple queries on same Factorization instantiation
    self.sol = None # most recent solution

	"""
	self.temp_f_list = [Factor(self.BN,var) for var in self.BN.V]
	map_list = []

	#### ORDER HANDLING ####
	if not order:
		order = copy.copy(self.BN.V)
		if isinstance(target,list):
			for t in target:
				order.remove(t)
		else: 
			order.remove(target)
	if isinstance(target,list):
		for t in target:
			if target in order:
				order.remove(t)
	else:
		if target in order:
			order.remove(target)

	##### EVIDENCE #####

	if len(evidence)>0:
		assert isinstance(evidence, dict), 'Evidence must be Dictionary'
		temp=[]
		for obs in evidence.items():
			for f in self.temp_f_list:
				if len(f.scope)>1 or obs[0] not in f.scope:
					temp.append(f)
				if obs[0] in f.scope:
					f.reduce_factor(obs[0],obs[1])
			order.remove(obs[0])
		self.temp_f_list=temp

	#### ALGORITHM ####
	for var in order:
		relevant_factors = [f for f in self.temp_f_list if var in f.scope]
		irrelevant_factors = [f for f in self.temp_f_list if var not in f.scope]

		# mutliply all relevant factors
		fmerge = relevant_factors[0]
		for i in range(1,len(relevant_factors)):
			fmerge.multiply_factor(relevant_factors[i])
		## only difference between marginal and map
		if marginal==False:
			map_list.append(copy.deepcopy(fmerge))
			fmerge.maxout_var(var)
		else:
			fmerge.sumout_var(var) # remove var from factor

		irrelevant_factors.append(fmerge) # add sum-prod factor back in
		self.temp_f_list = irrelevant_factors

	# Traceback MAP
	assignment={}
	for m in reversed(map_list):
		var = list(set(m.scope) - set(assignment.keys()))[0]
		m.reduce_factor_by_list([[k,v] for k,v in assignment.items() if k in m.scope and k!=var])
		assignment[var] = self.BN.data[var]['vals'][(np.argmax(m.cpt) / m.stride[var]) % m.card[var]]
	
	self.sol = assignment
	self.sol.update(evidence)
	print json.dumps(self.sol,indent=2)
	self.val=round(self.temp_f_list[0].cpt[0],4)









