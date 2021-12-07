include "globals.mzn";

int: w;   %  width of the silicon plate
int: n;   %  number of necessary circuits
set of int:Circuit=1..n;
array[Circuit] of 0..w :circuitWidth;  %  the width of every circuit
array[Circuit] of  int :circuitHeight;  %  the height of every circuit
int:maxHeight = sum(i in Circuit)(circuitHeight[i]); % sum of height
array[Circuit] of var 0..w :Xposition; %  circuit's Xposition on the coordinate
array[Circuit] of var 0..maxHeight :Yposition; %  circuit's Yposition on the coordinate

%width and height constraints
constraint forall(i in Circuit)
   ( Xposition[i] + circuitWidth[i] <= w /\ Xposition[i] >= 0 /\ Yposition[i] >= 0);



%noOverlap constraints
constraint 
    forall(i in Circuit)( 
        forall(j in Circuit where j > i)(
%             not(Xposition[i] >= Xposition[j] + circuitWidth[j]  \/ Xposition[i] + circuitWidth[i] <= Xposition[j]
%             \/ Yposition[i] >= Yposition[j] + circuitHeight[j] \/ Yposition[i] + circuitHeight[i] <= Yposition[j])
%             \/ not(Xposition[j] >= Xposition[i] + circuitWidth[i]  \/ Xposition[j] + circuitWidth[j] <= Xposition[i]
%             \/ Yposition[j] >= Yposition[i] + circuitHeight[i] \/ Yposition[j] + circuitHeight[j] <= Yposition[i])
%max（x1,x3）<=min(x2,x4)&&max(y1,y3)<=min(y2,y4)
              not(max(Xposition[i],Xposition[j]) < min(Xposition[i]+circuitWidth[i],Xposition[j]+ circuitWidth[j])
              /\max(Yposition[i],Yposition[j]) < min(Yposition[i]+circuitHeight[i],Yposition[j]+ circuitHeight[j]))
          )
      );  
      
      

%makespan as objective function
var int: height = max(i in Circuit)(Yposition[i] + circuitHeight[i]);

solve minimize height;


% output [
%     "PositionX   =", show([Xposition[i]| i in Circuit]), "\n",
%     "PositionY   =", show([Yposition[i]| i in Circuit]), "\n",
%     "Height = ", show(height), "\n"
% ];



