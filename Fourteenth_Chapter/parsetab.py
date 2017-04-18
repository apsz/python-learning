
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'nonassocFORALLEXISTSrightIMPLIESleftORleftANDrightNOTnonassocEQUALSSYMBOL COMMA EQUALS AND OR COLON NOT IMPLIES LPAREN RPAREN EXISTS FALSE TRUE FORALLFORMULA : FORALL SYMBOL COLON FORMULA\n                   | EXISTS SYMBOL COLON FORMULAFORMULA : TRUE\n                   | FALSEFORMULA : FORMULA IMPLIES FORMULA\n                   | FORMULA OR FORMULA\n                   | FORMULA AND FORMULAFORMULA : NOT FORMULAFORMULA : LPAREN FORMULA RPARENFORMULA : TERM EQUALS TERMFORMULA : SYMBOLTERM : SYMBOL LPAREN TERMLIST RPAREN\n                | SYMBOLTERMLIST : TERM COMMA TERMLIST\n                    | TERM'
    
_lr_action_items = {'SYMBOL':([0,2,3,7,9,10,13,14,15,16,22,27,30,],[1,1,12,17,1,20,20,1,1,1,1,1,20,]),'COMMA':([20,21,29,],[-13,30,-12,]),'NOT':([0,2,9,14,15,16,22,27,],[2,2,2,2,2,2,2,2,]),'EQUALS':([1,4,29,],[-13,13,-12,]),'EXISTS':([0,2,9,14,15,16,22,27,],[3,3,3,3,3,3,3,3,]),'AND':([1,5,6,8,11,18,20,23,24,25,26,28,29,31,32,],[-11,-3,15,-4,-8,15,-13,-10,15,-7,15,-9,-12,15,15,]),'COLON':([12,17,],[22,27,]),'FORALL':([0,2,9,14,15,16,22,27,],[7,7,7,7,7,7,7,7,]),'$end':([1,5,6,8,11,20,23,24,25,26,28,29,31,32,],[-11,-3,0,-4,-8,-13,-10,-5,-7,-6,-9,-12,-2,-1,]),'TRUE':([0,2,9,14,15,16,22,27,],[5,5,5,5,5,5,5,5,]),'IMPLIES':([1,5,6,8,11,18,20,23,24,25,26,28,29,31,32,],[-11,-3,14,-4,-8,14,-13,-10,14,-7,-6,-9,-12,14,14,]),'FALSE':([0,2,9,14,15,16,22,27,],[8,8,8,8,8,8,8,8,]),'OR':([1,5,6,8,11,18,20,23,24,25,26,28,29,31,32,],[-11,-3,16,-4,-8,16,-13,-10,16,-7,-6,-9,-12,16,16,]),'LPAREN':([0,1,2,9,14,15,16,20,22,27,],[9,10,9,9,9,9,9,10,9,9,]),'RPAREN':([1,5,8,11,18,19,20,21,23,24,25,26,28,29,31,32,33,],[-11,-3,-4,-8,28,29,-13,-15,-10,-5,-7,-6,-9,-12,-2,-1,-14,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'TERMLIST':([10,30,],[19,33,]),'TERM':([0,2,9,10,13,14,15,16,22,27,30,],[4,4,4,21,23,4,4,4,4,4,21,]),'FORMULA':([0,2,9,14,15,16,22,27,],[6,11,18,24,25,26,31,32,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> FORMULA","S'",1,None,None,None),
  ('FORMULA -> FORALL SYMBOL COLON FORMULA','FORMULA',4,'p_formula_quantifier','ply_flo2.py',134),
  ('FORMULA -> EXISTS SYMBOL COLON FORMULA','FORMULA',4,'p_formula_quantifier','ply_flo2.py',135),
  ('FORMULA -> TRUE','FORMULA',1,'p_formula_boolean','ply_flo2.py',139),
  ('FORMULA -> FALSE','FORMULA',1,'p_formula_boolean','ply_flo2.py',140),
  ('FORMULA -> FORMULA IMPLIES FORMULA','FORMULA',3,'p_formula_binary','ply_flo2.py',144),
  ('FORMULA -> FORMULA OR FORMULA','FORMULA',3,'p_formula_binary','ply_flo2.py',145),
  ('FORMULA -> FORMULA AND FORMULA','FORMULA',3,'p_formula_binary','ply_flo2.py',146),
  ('FORMULA -> NOT FORMULA','FORMULA',2,'p_formula_not','ply_flo2.py',150),
  ('FORMULA -> LPAREN FORMULA RPAREN','FORMULA',3,'p_formula_group','ply_flo2.py',154),
  ('FORMULA -> TERM EQUALS TERM','FORMULA',3,'p_formula_equals','ply_flo2.py',158),
  ('FORMULA -> SYMBOL','FORMULA',1,'p_formula_symbol','ply_flo2.py',162),
  ('TERM -> SYMBOL LPAREN TERMLIST RPAREN','TERM',4,'p_term','ply_flo2.py',166),
  ('TERM -> SYMBOL','TERM',1,'p_term','ply_flo2.py',167),
  ('TERMLIST -> TERM COMMA TERMLIST','TERMLIST',3,'p_termlist','ply_flo2.py',171),
  ('TERMLIST -> TERM','TERMLIST',1,'p_termlist','ply_flo2.py',172),
]