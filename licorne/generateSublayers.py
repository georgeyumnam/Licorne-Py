from __future__ import (absolute_import, division, print_function)
from licorne.layer import Layer, RoughnessModel
import numpy as np
import scipy.special as sci_sp
from scipy.integrate import quad
from copy import deepcopy

def J(model,xmin,xmax,scaling):
    if model=="TANH":
        return quad(lambda x: np.tanh(x*scaling),xmin,xmax)[0]
    if model=="ERFC":
        return quad(lambda x: sci_sp.erf(x*scaling),xmin,xmax)[0]

def rough_sublayer(layer_up,layer_down):
    """
    Function to calculate sublayers when there is roughness at the interface
    
    Args:
        layer_up   (Layer): The first layer (closer to surface)
        layer_down (Layer): The second layer
        
    Returns:
        tuple: list of sublayers, and a list of of ints (0 and 1), both the same length.
            If the int corresponding to index is 0, the sublayer belongs to layer_up 
    """
    
    #some constants
    alpha={"ERFC":sci_sp.erfinv(0.5)*2.,"TANH":np.arctanh(0.5)*2.}
    delta={"ERFC":sci_sp.erfinv(0.97),"TANH":np.arctanh(0.97)}
    #sigma is multiplied with 1.3 to correspond to Nevot-Croce roughness parameter 
    sigma=layer_down.roughness.value * 1.3 
    model=layer_down.roughness_model.name
    N=layer_down.sublayers
    
    if (model not in ["ERFC","TANH"]) or (N<2) or (sigma==0):
        half_layer_up=deepcopy(layer_up)
        half_layer_down=deepcopy(layer_down)
        half_layer_up.thickness.value*=0.5
        half_layer_down.thickness.value*=0.5
        return ([half_layer_up,half_layer_down],[0,1])
    scale=alpha[model]/sigma
    gamma=delta[model]/scale

    #first/last sublayer values. Only nsld_real,nsld_imaginary, and msld_rho are affected by rougness
    values_up=np.array([layer_up.nsld_real.value, layer_up.nsld_imaginary.value,layer_up.msld.rho.value])
    values_down=np.array([layer_down.nsld_real.value, layer_down.nsld_imaginary.value,layer_down.msld.rho.value])    

    #extracting layer thicknesses and calculate interface extent
    L_up=gamma
    L_down=L_up
    thickness_up=layer_up.thickness.value
    thickness_down=layer_down.thickness.value
    up_bound=None
    down_bound=None

    if gamma<thickness_up/2.:
        up_bound=thickness_up/2.-L_up #this part of the up layer is not changed
    else:
        L_up=thickness_up/2.
    
    if gamma<thickness_down/2.:
        down_bound=thickness_down/2.-L_down #this part of the down layer is not changed
    else:
        L_down=thickness_down/2.
    
    #adjust the values to account for non-symmetric distribution
    if (thickness_up<thickness_down) and (gamma>thickness_up/2):
        values_up=values_down-(values_down-values_up)*thickness_up/(L_down+L_up-J(model,-L_up,L_down,scale))
    if (thickness_up>thickness_down) and (gamma>thickness_down/2):
        values_down=values_up+(values_down-values_up)*thickness_down/(L_down+L_up+J(model,-L_up,L_down,scale))    
    #create sublayers
    sublayer_thickness=(L_up+L_down)/N
    sublayer_centers=np.linspace(-L_up+sublayer_thickness/2, L_down-sublayer_thickness/2,N)
    if model=="TANH":
        new_values=((values_down-values_up)[:,np.newaxis] * (np.tanh(scale*sublayer_centers)+1.)/2.).transpose()+values_up
    else:
        new_values=((values_down-values_up)[:,np.newaxis] * (sci_sp.erf(scale*sublayer_centers)+1.)/2.).transpose()+values_up
    sublayers_nsld_re,sublayers_nsld_im,sublayers_msld_rho=new_values.transpose()
    sublayers_msld_theta=[layer_up.msld.theta.value if x < 0 else layer_down.msld.theta.value for x in sublayer_centers]
    sublayers_msld_phi=[layer_up.msld.phi.value if x < 0 else layer_down.msld.phi.value for x in sublayer_centers]
    sublayer_list=[Layer(sublayer_thickness,nr,ni,mr,mt,mp,0,RoughnessModel.NONE,0) for nr,ni,mr,mt,mp in
                        zip(sublayers_nsld_re,sublayers_nsld_im,sublayers_msld_rho,sublayers_msld_theta,sublayers_msld_phi)]
    corresponding_layer=list(np.piecewise(sublayer_centers,[sublayer_centers<0,sublayer_centers>=0],[0,1]))
    
    #deal with rest of the half layers, outside of the rough region
    if up_bound is not None:
        sublayer_list.insert(0,Layer(up_bound,layer_up.nsld_real.value, layer_up.nsld_imaginary.value,layer_up.msld.rho.value,
                                     layer_up.msld.theta.value,layer_up.msld.phi.value,0,RoughnessModel.NONE,0))
        corresponding_layer.insert(0,0)
    if down_bound is not None:
        sublayer_list.append(Layer(down_bound,layer_down.nsld_real.value, layer_down.nsld_imaginary.value,layer_down.msld.rho.value,
                                   layer_down.msld.theta.value,layer_down.msld.phi.value,0,RoughnessModel.NONE,0))
        corresponding_layer.append(1)
    return (sublayer_list,corresponding_layer)

def generateSublayers(layerlist):
    sublayers=[]
    corresponding=[]
    for i in range(len(layerlist)-1):
        s,c=rough_sublayer(layerlist[i],layerlist[i+1])
        sublayers+=s
        corresponding+=[j+i for j in c]
    return (sublayers,corresponding)

if __name__=='__main__':
    Incoming=Layer(thickness=np.inf,
                 nsld_real=0,
                 nsld_imaginary=0,
                 msld_rho=0,
                 msld_theta=0,
                 msld_phi=90,
                 roughness=0,
                 roughness_model=RoughnessModel.NONE,
                 sublayers=16)
    Layer1=Layer(thickness=20.,
                 nsld_real=1.6139e-6,
                 nsld_imaginary=-3e-8,
                 msld_rho=0,
                 msld_theta=0,
                 msld_phi=90,
                 roughness=5.,
                 roughness_model=RoughnessModel.TANH,
                 sublayers=16)
    Layer2=Layer(thickness=20.,
                 nsld_real=3.3176e-6,
                 nsld_imaginary=-3e-8,
                 msld_rho=0,
                 msld_theta=0,
                 msld_phi=90,
                 roughness=5.,
                 roughness_model=RoughnessModel.NONE,
                 sublayers=16)
    Layer3=Layer(thickness=20,
                 nsld_real=2.2064e-006,
                 nsld_imaginary=-3e-8,
                 msld_rho=2.30455e-006,
                 msld_theta=0,
                 msld_phi=90,
                 roughness=50,
                 roughness_model=RoughnessModel.TANH,
                 sublayers=16)
    Substrate=Layer(thickness=np.inf,
                 nsld_real=3.533e-006,
                 nsld_imaginary=0,
                 msld_rho=0,
                 msld_theta=0,
                 msld_phi=0,
                 roughness=1.,
                 roughness_model=RoughnessModel.NONE,
                 sublayers=16)           

    layers=[Incoming,Layer1,Layer2,Layer3,Substrate]
    sublayers,corresponding=generateSublayers(layers)
    """sublayers=[]
    corresponding=[]
    for i in range(len(layers)-1):
        s,c=rough_sublayer(layers[i],layers[i+1])
        sublayers+=s
        corresponding+=[j+i for j in c]
    """
    for sl,cor in zip(sublayers,corresponding):
        print(cor,sl.thickness.value,sl.nsld_real.value,sl.nsld_imaginary.value,sl.msld.rho.value,sl.msld.theta.value,sl.msld.phi.value)    
    
    
    thick=[sl.thickness.value for sl in sublayers]
    #print(thick,corresponding)
    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.cm
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    with PdfPages('NSLD.pdf') as pdf:
        fig,ax=plt.subplots()    
        depth=np.array(thick)
        thickmax=depth[np.isfinite(depth)].max()
        depth[np.isinf(depth)]=thickmax
        th1=depth[corresponding.index(1)]
        depth=depth.cumsum()
        depth-=depth[corresponding.index(1)]-th1
        print(thickmax)
        depth=np.insert(depth,0,depth[0]-thickmax)
        #depth=np.append(depth,depth[-1]+thickmax)
        val=np.array([sl.nsld_imaginary.value for sl in sublayers])
        patches=[]
        for i,v in enumerate(val):
            polygon=Polygon([[depth[i],0.],[depth[i],v],[depth[i+1],v],[depth[i+1],0]],True)
            patches.append(polygon)
        p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4, picker=True)
        colors = 100*np.random.rand(len(patches))
        p.set_array(np.array(corresponding))
        ax.plot(depth[1:],val,visible=False)
        ax.add_collection(p)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        ax.set_xlabel('Depth')
        ax.set_ylabel('NSLD')
        
        fig.tight_layout()
        pdf.savefig(fig)
    plt.close()


