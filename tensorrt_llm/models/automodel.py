from typing import Optional

from ..mapping import Mapping
from . import MODEL_MAP
from .modeling_utils import QuantConfig


class AutoConfig:

    @staticmethod
    def from_hugging_face(hf_model_or_dir,
                          dtype: str = 'auto',
                          mapping: Optional[Mapping] = None,
                          quant_config: Optional[QuantConfig] = None,
                          **kwargs):
        import transformers

        hf_config = transformers.AutoConfig.from_pretrained(
            hf_model_or_dir, trust_remote_code=True)

        if hasattr(hf_config,
                   'architectures') and hf_config.architectures is not None:
            hf_arch = hf_config.architectures[0]
        elif hasattr(hf_config,
                     'model_type') and hf_config.model_type.find('mamba') != -1:
            hf_arch = 'MambaForCausalLM'

        trtllm_model_cls = MODEL_MAP.get(hf_arch, None)
        if trtllm_model_cls is None:
            raise NotImplementedError(
                f"The given huggingface model architecture {hf_arch} is not supported in TRT-LLM yet"
            )

        if not hasattr(trtllm_model_cls, 'config_class'):
            raise NotImplementedError(
                f"The given TRT-LLM model class {trtllm_model_cls} does not support AutoConfig"
            )

        trtllm_cfg_cls = getattr(trtllm_model_cls, 'config_class')
        if not hasattr(trtllm_cfg_cls, 'from_hugging_face'):
            raise NotImplementedError(
                f"The given TRT-LLM model class {trtllm_cfg_cls} does not support from_hugging_face"
            )

        return trtllm_cfg_cls.from_hugging_face(hf_model_or_dir, dtype, mapping,
                                                quant_config, **kwargs)


class AutoModelForCausalLM:

    @staticmethod
    def get_trtllm_model_class(hf_model_or_dir, trust_remote_code=False):
        import transformers

        hf_config = transformers.AutoConfig.from_pretrained(
            hf_model_or_dir, trust_remote_code=trust_remote_code)

        if hasattr(hf_config,
                   'architectures') and hf_config.architectures is not None:
            hf_arch = hf_config.architectures[0]
        elif hasattr(hf_config,
                     'model_type') and hf_config.model_type.find('mamba') != -1:
            hf_arch = 'MambaForCausalLM'

        trtllm_model_cls = MODEL_MAP.get(hf_arch, None)

        if trtllm_model_cls is None:
            raise NotImplementedError(
                f"The given huggingface model architecture {hf_arch} is not supported in TRT-LLM yet"
            )
        return trtllm_model_cls

    @staticmethod
    def from_hugging_face(hf_model_or_dir,
                          dtype: str = 'auto',
                          mapping: Optional[Mapping] = None,
                          quant_config: Optional[QuantConfig] = None,
                          **kwargs):
        trtllm_model_cls = AutoModelForCausalLM.get_trtllm_model_class(
            hf_model_or_dir)

        if not hasattr(trtllm_model_cls, 'from_hugging_face'):
            raise NotImplementedError(
                f"The given {trtllm_model_cls} does not support from_hugging_face yet"
            )

        return trtllm_model_cls.from_hugging_face(hf_model_or_dir, dtype,
                                                  mapping, quant_config,
                                                  **kwargs)
