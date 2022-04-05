include "globals.mzn";

int: w;   %  width of the silicon plate
int: n;   %  number of necessary circuits
set of int:Circuit=1..n;
array[Circuit] of 0..w:width;  %  the width of every circuit
array[Circuit] of int:height;  %  the height of every circuit
int:maxHeight = sum(i in Circuit)(max(width[i],height[i])); % max height in rotation
array[Circuit] of var 0..w:x; %  circuit's X on the coordinate
array[Circuit] of var 0..maxHeight:y; %  circuit's Y on the coordinate
array[Circuit] of var bool: rotation;
% if rotate, circuit's width will be height
array[Circuit] of var 0..w: width_r = [if rotation[i] then height[i] else width[i] endif | i in Circuit];
array[Circuit] of var int: height_r = [if rotation[i] then width[i] else height[i] endif | i in Circuit];

%non-decreasing order 
array[int] of int: circuitOrder = sort_by(Circuit,[-width[i] * height[i] | i in Circuit]);
var 0..maxHeight: h;
 
%width and height constraints
% maximum width
constraint max([x[i] + width_r[i] | i in Circuit]) <= w;
% maximum heigth
constraint max([y[i] + height_r[i] | i in Circuit]) = h;
% a circuit cannot be rotated if its height is greater than w
constraint forall(i in Circuit)(height[i] > w -> rotation[i]==false);
% a circuit with same width and height should not be rotated
constraint forall (i in Circuit) (width[i] = height[i] -> rotation[i]==false);

constraint cumulative(y, height_r, width_r, w);
constraint cumulative(x, width_r, height_r, h);
%no overlap
constraint diffn(x, y, width_r, height_r); 


%Remove the gap
constraint
forall(r in Circuit)(
member([0] ++ [x[i] + width_r[i] | i in Circuit where i != r], x[r]) /\
member([0] ++ [y[i] + height_r[i] | i in Circuit where i != r], y[r]));

%symmetry breaking constraint
constraint
let {int: o1 = circuitOrder[1], int: o2 = circuitOrder[2]}
in lex_less([y[o1],x[o1]], [y[o2],x[o2]]);

% symmetry breaking
constraint forall(r in Circuit)(let {array[int] of int: R = [i | i in Circuit where (width[i]=width[r]
            /\ height[i]=height[r]) \/ (width[i]=height[r] /\ height[i]=width[r])]} 
            in if length(R)>1 /\ min(R)=r then 
            forall(i in index_set(R) where i>1)(
             lex_less([y[R[i-1]],x[R[i-1]]], [y[R[i]],x[R[i]]])
            )
            else true endif
);


solve 
::int_search([y[r] | r in circuitOrder], input_order, indomain_min,complete)
:: int_search([x[r] | r in circuitOrder], input_order, indomain_min,complete)
::int_search([h], input_order, indomain_min, complete)
minimize h;




