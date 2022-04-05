include "globals.mzn";

int: w;   %  width of the silicon plate
int: n;   %  number of necessary circuits
set of int:Circuit=1..n;
array[Circuit] of 0..w :width;  %  the width of every circuit
array[Circuit] of  int :height;  %  the height of every circuit
int:maxHeight = sum(height); % sum of height
array[Circuit] of var 0..w-min(width) :x; %  circuit's X on the coordinate
array[Circuit] of var 0..maxHeight-min(height) :y; %  circuit's Y on the coordinate
%non-decreasing order 
array[int] of int: circuitOrder = sort_by(Circuit,[-width[i] * height[i] | i in Circuit]);
var max(height)..maxHeight: h;
 
%width and height constraints
% maximum width
constraint max([x[i] + width[i] | i in Circuit]) <= w;
% maximum heigth
constraint max([y[i] + height[i] | i in Circuit]) = h;

constraint cumulative(y, height, width, w);
constraint cumulative(x, width, height, h);
%no overlap
constraint diffn(x, y, width, height); 

%Remove the gap
constraint
forall(r in Circuit)(
member([0] ++ [x[i] + width[i] | i in Circuit where i != r], x[r]) /\
member([0] ++ [y[i] + height[i] | i in Circuit where i != r], y[r]));

%symmetry breaking constraint
constraint
let {int: c1 = circuitOrder[1], int: c2 = circuitOrder[2]}
in lex_less([y[c1],x[c1]], [y[c2],x[c2]]);


% symmetry breaking for circuit with same width and height
constraint forall(r in Circuit)(let {array[int] of int: R = [i | i in Circuit where width[i]=width[r]
            /\ height[i]=height[r]]} 
            in if length(R)>1 /\ min(R)=r then 
            forall(i in index_set(R) where i>1)(
             lex_less([y[R[i-1]],x[R[i-1]]], [y[R[i]],x[R[i]]])
            )
            else true endif
);




solve 
::int_search([y[r] | r in circuitOrder], input_order, indomain_random,complete)
:: int_search([x[r] | r in circuitOrder], input_order, indomain_random,complete)
::int_search([h], input_order, indomain_random, complete)
::restart_geometric(1.5,100)
minimize h;



