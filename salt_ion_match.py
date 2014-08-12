'''
pyEQL salt matching library

This file contains functions that allow a pyEQL Solution object composed of
individual species (usually ions) to be mapped to a solution of one or more
salts. This mapping is necessary because some parameters (such as activity
coefficient data) can only be determined for salts (e.g. NaCl) and not individual
species (e.g. Na+)

'''
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

import chemical_formula as chem

def _sort_components(Solution):
    '''
    Sort the components of a solution in descending order (by mole fraction).
    
    Parameters:
    ----------
    Solution : Solution object
    
    Returns:
    -------
    A list whose keys are the component names (formulas) and whose
    values are the component objects themselves
    
    
    '''
    formula_list = []
        
    # populate a list with component names
    for item in Solution.components:
        formula_list.append(item)
        
    # populate a dictionary with formula:concentration pairs
    mol_list={}
    for item in Solution.components.keys():
        mol_list.update({item:Solution.get_amount(item,'mol')})
    
    return sorted(formula_list,key=mol_list.__getitem__,reverse=True)
    
def identify_salt(Solution):
    '''
    Analyze the components of a solution and identify the salt that most closely
    approximates it.
    (e.g., if a solution contains 0.5 mol/kg of Na+ and Cl-, plus traces of H+
    and OH-, the matched salt is 0.5 mol/kg NaCl)
    
    Returns:
    -------
    A string representing the chemical formula of the salt
    '''
    # sort the components by moles
    sort_list = _sort_components(Solution)
   
    cation = ''
    anion = ''    
    
    # warn if something other than water is the predominant component    
    if sort_list[0] != 'H2O':
        logger.warning('H2O is not the most prominent component')
        return None
    else:    
    # take the dominant cation and anion and assemble a salt from them
        for item in sort_list[0:]:
            if chem.get_formal_charge(item) > 0 and cation == '':
                cation = item
            elif chem.get_formal_charge(item) < 0 and anion == '':
                anion = item
            else:
                pass
            
    # assemble the salt
    salt_formula = build_salt(cation,anion)
    return salt_formula

def build_salt(cation,anion):
    '''
    Generate a chemical formula for a salt based on its component ions
    
    Parameters:
    ----------
    cation, anion : str
            Chemical formula of the cation and anion, respectively
    
    Returns:
    -------
    str : A string representing the chemical formula of the salt
    
    Examples:
    --------
    >>> build_salt('Na+','Cl-')
    'NaCl'
    >>> build_salt('Mg+2','Cl-')
    'NaCl'
    >>> build_salt('Fe+3','SO4-2')
    'Fe(SO4)2'
    >>> build_salt('Fe+2','SO4-2')
    'FeSO4'    
    
    '''
    # get the charges on cation and anion
    z_cation = chem.get_formal_charge(cation)
    z_anion = chem.get_formal_charge(anion)
    
    # assign stoichiometric coefficients by finding a common multiple
    nu_cation = abs(z_anion)
    nu_anion = abs(z_cation)
    
    # if both coefficients are the same, set each to one
    if nu_cation == nu_anion:
        nu_cation = 1
        nu_anion = 1
        
    # start building the formula, cation first
    salt_formula=''
    if nu_cation > 1:
        salt_formula+='('
        salt_formula+= _trim_formal_charge(cation)
        salt_formula+=')'
        salt_formula+=str(nu_cation)
    else:
        salt_formula+= _trim_formal_charge(cation)
    
    if nu_anion > 1:
        salt_formula+='('
        salt_formula+= _trim_formal_charge(anion)
        salt_formula+=')'
        salt_formula+=str(nu_anion)
    else:
        salt_formula+= _trim_formal_charge(anion)
    
    return salt_formula
    
def _trim_formal_charge(formula):
    '''
    remove the formal charge from a chemical formula
    
    Examples:
    --------
    >>> _trim_formal_charge('Fe+++')
    'Fe'
    >>> _trim_formal_charge('SO4-2')
    'SO4'
    >>> _trim_formal_charge('Na+')
    'Na'
    
    '''
    charge = chem.get_formal_charge(formula)
    output = ''
    if charge > 0:
        output = formula.split('+')[0]
    elif charge < 0:
        output = formula.split('-')[0]

    return output

# TODO - turn doctest back on when the nosigint error is gone        
#if __name__ == "__main__":
 #   import doctest
  #  doctest.testmod()