class slicer_ACPCTransform:
    """
    Note:
        dependencies: Nipype,registration
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.registration.specialized import ACPCTransform
        at = ACPCTransform()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputTransform(self) -> None:
        return self.res.outputs.outputTransform

###############################################################################


class slicer_AffineRegistration:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.registration import AffineRegistration
        at = AffineRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputtransform(self) -> None:
        return self.res.outputs.outputtransform

    def resampledmovingfilename(self) -> None:
        return self.res.outputs.resampledmovingfilename

###############################################################################


class slicer_BRAINSDemonWarp:
    """
    Note:
        dependencies: Nipype,registration
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.registration.specialized import BRAINSDemonWarp
        at = BRAINSDemonWarp()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

    def outputDisplacementFieldVolume(self) -> None:
        return self.res.outputs.outputDisplacementFieldVolume

    def outputCheckerboardVolume(self) -> None:
        return self.res.outputs.outputCheckerboardVolume

###############################################################################


class slicer_BSplineDeformableRegistration:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.registration import BSplineDeformableRegistration
        at = BSplineDeformableRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputtransform(self) -> None:
        return self.res.outputs.outputtransform

    def outputwarp(self) -> None:
        return self.res.outputs.outputwarp

    def resampledmovingfilename(self) -> None:
        return self.res.outputs.resampledmovingfilename

###############################################################################


class slicer_BSplineToDeformationField:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.converters import BSplineToDeformationField
        at = BSplineToDeformationField()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def defImage(self) -> None:
        return self.res.outputs.defImage

###############################################################################


class slicer_IntensityDifferenceMetric:
    """
    Note:
        dependencies: Nipype,quantification
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.quantification.changequantification import IntensityDifferenceMetric
        at = IntensityDifferenceMetric()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

    def reportFileName(self) -> None:
        return self.res.outputs.reportFileName

###############################################################################


class slicer_DWIUnbiasedNonLocalMeansFilter:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.diffusion.denoising import DWIUnbiasedNonLocalMeansFilter
        at = denoising.DWIUnbiasedNonLocalMeansFilter()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

###############################################################################


class slicer_ExpertAutomatedRegistration:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.registration import ExpertAutomatedRegistration
        at = ExpertAutomatedRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def resampledImage(self) -> None:
        return self.res.outputs.resampledImage

    def saveTransform(self) -> None:
        return self.res.outputs.saveTransform

###############################################################################


class slicer_FiducialRegistration:
    """
    Note:
        dependencies: Nipype,registration
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.registration.specialized import FiducialRegistration
        at = FiducialRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def saveTransform(self) -> None:
        return self.res.outputs.saveTransform

###############################################################################


class slicer_LinearRegistration:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.registration import LinearRegistration
        at = LinearRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputtransform(self) -> None:
        return self.res.outputs.outputtransform

    def resampledmovingfilename(self) -> None:
        return self.res.outputs.resampledmovingfilename

###############################################################################


class slicer_MultiResolutionAffineRegistration:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.registration import MultiResolutionAffineRegistration
        at = MultiResolutionAffineRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def resampledImage(self) -> None:
        return self.res.outputs.resampledImage

    def saveTransform(self) -> None:
        return self.res.outputs.saveTransform

###############################################################################


class slicer_OtsuThresholdImageFilter:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.filtering import OtsuThresholdImageFilter
        at = OtsuThresholdImageFilter()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

###############################################################################


class slicer_PETStandardUptakeValueComputation:
    """
    Note:
        dependencies: Nipype,quantification
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.quantification.petstandarduptakevaluecomputation import PETStandardUptakeValueComputation
        at = PETStandardUptakeValueComputation()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def csvFile(self) -> None:
        return self.res.outputs.csvFile

###############################################################################


class slicer_ResampleScalarVolume:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.filtering import ResampleScalarVolume
        at = ResampleScalarVolume()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def OutputVolume(self) -> None:
        return self.res.outputs.OutputVolume

###############################################################################


class slicer_RigidRegistration:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.registration import RigidRegistration
        at = RigidRegistration()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputtransform(self) -> None:
        return self.res.outputs.outputtransform

    def resampledmovingfilename(self) -> None:
        return self.res.outputs.resampledmovingfilename

###############################################################################


class slicer_OtsuThresholdSegmentation:
    """
    Note:
        dependencies: Nipype,legacy
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.legacy.segmentation import OtsuThresholdSegmentation
        at = OtsuThresholdSegmentation()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

###############################################################################


class slicer_VBRAINSDemonWarp:
    """
    Note:
        dependencies: Nipype,registration
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.registration.specialized import VBRAINSDemonWarp
        at = VBRAINSDemonWarp()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

    def outputDisplacementFieldVolume(self) -> None:
        return self.res.outputs.outputDisplacementFieldVolume

    def outputCheckerboardVolume(self) -> None:
        return self.res.outputs.outputCheckerboardVolume

###############################################################################


class slicer_BRAINSFit:
    """
    Note:
        dependencies: Nipype,registration
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.registration.brainsfit import BRAINSFit
        at = BRAINSFit()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def bsplineTransform(self) -> None:
        return self.res.outputs.bsplineTransform

    def linearTransform(self) -> None:
        return self.res.outputs.linearTransform

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

    def outputFixedVolumeROI(self) -> None:
        return self.res.outputs.outputFixedVolumeROI

    def outputMovingVolumeROI(self) -> None:
        return self.res.outputs.outputMovingVolumeROI

    def strippedOutputTransform(self) -> None:
        return self.res.outputs.strippedOutputTransform

    def outputTransform(self) -> None:
        return self.res.outputs.outputTransform

###############################################################################


class slicer_BRAINSResample:
    """
    Note:
        dependencies: Nipype,registration
        GUI: no
        link_web: (click Ctrl + U)
    """
    def __init__(self, **options):
        from nipype.interfaces.slicer.registration.brainsresample import BRAINSResample
        at = BRAINSResample()
        for ef in options:
            setattr(at.inputs, ef, options[ef])
        self.res = at.run()

    def outputVolume(self) -> None:
        return self.res.outputs.outputVolume

###############################################################################


