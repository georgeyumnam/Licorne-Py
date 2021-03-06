Theta1=0.0068;Theta2=0.01;Theta3=0.017;
DTheta1=0.0003;DTheta2=0.0005;DTheta3=0.0009;
Q1=0.03;Q2=0.045;QP1=Q<Q1;QP2=(Q>=Q1)&(Q<=Q2);QP3=Q>Q2;
DLambda=0.005; Lambda=Q.*0; Sigma=Q.*0;
Lambda(QP1)=4*pi*sin(Theta1)./Q(QP1); 
Lambda(QP2)=4*pi*sin(Theta2)./Q(QP2);
Lambda(QP3)=4*pi*sin(Theta3)./Q(QP3);  
Sigma(QP1)=Q(QP1).*sqrt((DTheta1/Theta1)^2+(DLambda./Lambda(QP1)).^2);
Sigma(QP2)=Q(QP2).*sqrt((DTheta2/Theta2)^2+(DLambda./Lambda(QP2)).^2); 
Sigma(QP3)=Q(QP3).*sqrt((DTheta3/Theta3)^2+(DLambda./Lambda(QP3)).^2);
