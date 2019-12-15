# -*- coding: utf-8 -*-

from src.qa4sm_reader.handlers import _build_fname_templ, _metr_grp

def test_build_fname_templ():
    templ = _build_fname_templ(2)
    assert templ == '{i_ref}-{ref}.{ref_var}_with_{i_ds1}-{ds1}.{var1}.nc'
    templ = _build_fname_templ(3)
    assert templ == '{i_ref}-{ref}.{ref_var}_with_{i_ds1}-{ds1}.{var1}' \
                    '_with_{i_ds2}-{ds2}.{var2}.nc'
    templ = _build_fname_templ(4)
    assert templ == '{i_ref}-{ref}.{ref_var}_with_{i_ds1}-{ds1}.{var1}' \
                    '_with_{i_ds2}-{ds2}.{var2}_with_{i_ds3}-{ds3}.{var3}.nc'
    templ = _build_fname_templ(5)
    assert templ == '{i_ref}-{ref}.{ref_var}_with_{i_ds1}-{ds1}.{var1}' \
                    '_with_{i_ds2}-{ds2}.{var2}_with_{i_ds3}-{ds3}.{var3}' \
                    '_with_{i_ds4}-{ds4}.{var4}.nc'
    templ = _build_fname_templ(6)
    assert templ == '{i_ref}-{ref}.{ref_var}_with_{i_ds1}-{ds1}.{var1}' \
                    '_with_{i_ds2}-{ds2}.{var2}_with_{i_ds3}-{ds3}.{var3}' \
                    '_with_{i_ds4}-{ds4}.{var4}_with_{i_ds5}-{ds5}.{var5}.nc'

def test_metr_grp():
    assert _metr_grp('asdf') is None

    assert _metr_grp('n_obs') == 0
    
    assert _metr_grp('R') == 2
    assert _metr_grp('p_R') == 2
    assert _metr_grp('rho') == 2
    assert _metr_grp('p_rho') == 2
    assert _metr_grp('RMSD') == 2
    assert _metr_grp('BIAS') == 2
    assert _metr_grp('urmsd') == 2
    assert _metr_grp('mse') == 2
    assert _metr_grp('mse_corr') == 2
    assert _metr_grp('mse_bias') == 2
    assert _metr_grp('mse_var') == 2
    assert _metr_grp('RSS') == 2
    assert _metr_grp('tau') == 2
    assert _metr_grp('p_tau') == 2
    
    assert _metr_grp('snr') == 3
    assert _metr_grp('beta') == 3
    assert _metr_grp('err_std') == 3


if __name__ == '__main__':
    test_build_fname_templ()
    test_metr_grp()