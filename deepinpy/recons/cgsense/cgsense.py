#!/usr/bin/env python

import torch

from deepinpy.utils import utils
from deepinpy.opt import ConjGrad
from deepinpy.forwards import MultiChannelMRI
from deepinpy.recons import Recon

class CGSenseRecon(Recon):

    def __init__(self, args):
        super(CGSenseRecon, self).__init__(args)
        self.l2lam = torch.nn.Parameter(torch.tensor(args.l2lam_init))
        self.A = None

    def batch(self, data):

        maps = data['maps']
        masks = data['masks']
        inp = data['out']

        self.A = MultiChannelMRI(maps, masks, l2lam=0., img_shape=data['imgs'].shape, use_sigpy=self.use_sigpy, noncart=self.noncart)
        self.x_adj = self.A.adjoint(inp)

    def forward(self, y):
        cg_op = ConjGrad(self.x_adj, self.A.normal, l2lam=self.l2lam, max_iter=self.cg_max_iter, eps=self.eps, verbose=False)
        x_out = cg_op.forward(self.x_adj)
        self.num_cg = cg_op.num_cg
        return x_out

    def get_metadata(self):
        return {
                'num_cg': self.num_cg,
                }
