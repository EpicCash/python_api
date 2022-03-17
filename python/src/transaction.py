from datetime import datetime
from typing import Union


class Transaction:
    """
    // Object to store instance of epic-cash transaction //
    :param destination: STR, valid URL address, file name or TOR/epic-box address
    :param method: STR, ['http', 'file', 'tor', 'keybase', 'epic-box'] - transaction method
    :param amount: INT/FLOAT/STR, transaction value (+ fees)
    :param message: STR, Optional, message carried with transaction, not saved on blockchain
    :param strategy: STR, ['smallest', 'all'] - manage outputs used for transaction
    :param created: Datetime, Datetime object in moment of creating transaction
    :param executed: Datetime, Datetime object in moment of executing transaction
    """

    def __init__(self,
                 destination: str,
                 method: str = 'http',
                 amount: Union[int, float, str] = 0,
                 message: str = '',
                 strategy: str = 'smallest',
                 created: Union[datetime, str, bool] = False,
                 executed: Union[datetime, str, bool] = False
                 ):
        self.destination = destination
        self.strategy = strategy
        self.message = message
        self.amount = str(amount)
        self.method = method
        self.created = created
        self.executed = executed
        self.data: dict = {}

        if 'file' in self.method and 'http' in self.destination:
            print(f'Warning: "{self.destination}" looks like HTTP/S address '
                  f'but transaction method is: "{self.method}"')

        if 'file' in self.method and not self.destination.endswith('.tx'):
            self.destination = f"{self.destination}.tx"

        # print(self.__dict__)

    def validate(self):
        return (len(self.destination) > 3 and
                isinstance(self.amount, (int, float, str)) and
                self.created and self.strategy and self.method)


"""
V2 SLATEPACKS

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 \\ -- TRANSACTION FILE STEP I -- \\
  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

{
   "version_info":{
      "version":2,
      "orig_version":2
   },
   "num_participants":2,
   "id":"75e9609b-71ef-4179-9b74-3b049f02e86f",
   "tx":{
      "offset":"0ad9f2999c55a09e66c5b538959dea78be863782df3f1bb003c6dbc123b1b90c",
      "body":{
         "inputs":[
            {
               "features":"Plain",
               "commit":"095f752ca92d7d763d02b8db6e32e3b2ee95a0e69c5db1e88a12677d5cdfba4313"
            }
         ],
         "outputs":[
            {
               "features":"Plain",
               "commit":"0887630c788cf62b44589362a26eb6f4f174eef0df4bef884c07305c076b8a7d59",
               "proof":"602fab0f553c271c24b33e55b489ad59feba919de236e0757764676770071f10a3eb86cbc7bdbe19879aa8d67d00c708bf6190716bfdd57c4cfda3375dcb11660c7d4ff42dd0afc4d9745da1bca5291c36e1640e65b533515a633ff5f0accd966555a738d94f36bbd297b55229a370b3f9da85f17f27c9dfa2dc57c67540fb90a51a2bf9c08aff27d7445e93c1dc235fcd3cbf8eb828075471d5117c73fa947d1c9cb94825c1136f0ac2b70e356ecaebbdc4984ae82ed788d9aa20c2b5c038a84d1e04792aaf0da199ef7488a2019dca1b4fa0b2e1e4744d5465f863d7af8751f515c502382fa89b829621ede0f80c7f184c58b2b1aaefd3978a21d11660584ea7453ce2a66013abedbaca9a4d19c4011564e883715da55054d13e19b869c82d67e6329a1a40154f18a996d0440c13f07a5d5d5f133c552c18ff71c48f892bebdf1a17854f8e3f35a2a86878f37d7045ddcf101f02ff5e78a593fec6e581fb3e2ba3028a65c224fb462aee156d7e4875cd5110209efebede1dcb6e0cfbfe3ff9aa15fb3b5c698457ceae04d526dceada9d292687b8b125ebc662b3f8a55001301fcffb42d3555234ef67b26bc2d8d742b64e29fb023cc8e5d036b075f9e866e7c38272858344e8be044609c7aaa0d089856319c7fad7b257bc0ba6db6db272270910b0fd2d15fe1610fc71300db175f99d041e9d5d346bfcc6ea24f0dc639acfc7e305be16a2aa01e1ed00b6162087b445b5d5c9153bedd6c9536dce00ce24a5a59a0e6603c1750ba7e2a741892d3c6141cf511bc8b2b64e21a71efb313b991a88c31c2a20e6c2aebf2e93ecad3a8793fe84a3f44f3243db5493d2a54557c629d6fb2c738245e0659b1dbb76371eb808adf96e1f7fb017626f785a9cf318911e6c4a6cc208d2f45e94df5bcadb419f2aa9a31f9502d8234a3503c2db7378eb6100115d"
            }
         ],
         "kernels":[
            {
               "features":"Plain",
               "fee":"800000",
               "lock_height":"0",
               "excess":"000000000000000000000000000000000000000000000000000000000000000000",
               "excess_sig":"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            }
         ]
      }
   },
   "amount":"10000000",
   "fee":"800000",
   "height":"1347224",
   "lock_height":"0",
   "participant_data":[
      {
         "id":"0",
         "public_blind_excess":"02a6e8d8c8ddda49b7437ce9d19374452b89bdb5c1344614f687262b0951287506",
         "public_nonce":"03374ea7ee158127156e97092ca6c08aeb2dc3fdab62391feea426c89df18dd717",
         "part_sig":null,
         "message":"testing python",
         "message_sig":"caa5f181ba08828c873bf3b30306c48a25c58f63a19c12a9ab08803ce5055200642661954316f007a2b52907171c1d8ee2f9a15aa930c9d11068db9c5ba450be"
      }
   ]
}


\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
\\ -- TRANSACTION FILE (RESPONSE) STEP II -- \\
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
[
   {
      "version_info":{
         "version":2,
         "orig_version":2
      },
      "num_participants":2,
      "id":"d12df9b4-1ccd-4467-a716-d6f342994039",
      "tx":{
         "offset":"2a04bfe2836e4d0aa2d82a1acd7ddca72a23957be33bee26f5811ca585b8398a",
         "body":{
            "inputs":[
               {
                  "features":"Plain",
                  "commit":"084aa5bfec1a38b88f110c32bec7f16575ff9f79f750b492fdd3e1bdad4262127b"
               }
            ],
            "outputs":[
               {
                  "features":"Plain",
                  "commit":"08809a4211263f183657d7b598ab967d4ffb96eff19ddd6902c972e6817ed7e54f",
                  "proof":"0ceff0b7e10f1dc1d873314fa9dced856b1f9914f0ad55821833ac8ebbab349d4eab53d3139f4cf744caacb5953c7932be77a105b85eb6dcbd4bda1338ef961c0d92fac959be4c0451c4678542391f4a974e87d3ead3aa86137af3acb76faceaf2a9de14590e83e77085e71e20f57ed4021384d24467e4ce68d36979f92b0699dcc5cc764cffcc015b9ecc44dca569921764cced296ff222dd9e6049d07c96f602c90bbc89b7680d570f61c69f61333c1beae88f910c21c18df83c839f3fb86c53be592efb1523c41abf9b31bedb0f9e8ae20aa53169fe117de1e27024984a1d52b9c1807716c26916c3724750df2ced2f81f909f165bf0930eb23e5137ad6eaee6d55386664946d378218cda20fd340963336279f6005f42edaaeba6d8b5843259f20ab74fc8b606ea43411a035b0f4d662f9f89ddc329225da8e1ff214ef1657d11de9357d5b1967a105c7735989c337297f252a3ff47584bad3fc8ee89d0aaeb702edc25031b6d1954d8bd0c6cedcec00431de78e3668cf78f35bd3f199c6e79b406a452a8c5856eb9516a5f3c0799dc0e5b4310dc3483dfec43982e7401aabdb74616cfeb18f786b8643ba8bc0a2c73ebdcb9903b6e4a7dcfd4290f9a1cc32ed08176f444e1fe7603ff2c34d11c2a52490387f87701d27513e3c7f42795fda9db149a4f274348841343225e93e813213f2cec96cc4295356f234ac86fbfc7c27a0ea81cebc025a5cc9d9568f5bcf434e0986e27314f20e456608d47c428361be6580371bb81c79f2c8c3988ac2ad79b3bb153bbf2d2cfeade20f9f97529539e1696c274b41b51d6948e332e93da4202c84dad5447ea0afa87f97f02b168a0b120a0fd5fb5f2a1e89c0594bfdd89389279e439c47816fe62ce0213cb2a36a958676faff8942646b3f82474067cc2e9e691d65212a740455c9c233345ac6af4791b7"
               },
               {
                  "features":"Plain",
                  "commit":"08172533373353d6b351a57bcc5758fb91f893750e3b342617ce09825bb06071df",
                  "proof":"6ad795b78f4c68a021fa3328474c0cb1a9ed5d028aaeac178d6207b4425553ddb4a1742e2c01abbacb9e4f7ae8768d5b5d547502da7722bb36395159310f764a07737d4b1fba9ea1255331db2d3cad0de7e4a6a5b20d2602aa078bba90c4a3d97e0ff53ac089b72f790141735fecb342865e8dffa7a6ad2dd65b213fa66c25d4dcdb452e8857f7c2d3ffe6af6ee51494bd94ae2765ca4b7d1fcc7ae4061ae5f719105d251e627f6894e8df3391844b52628b5b0a2db51b68e24e11f8613eaeca07f5320227aff4b0a91739e6bb7bdf1ffe05e5d7b474d1ee2fe06ca7b975711b04b92164e3cf9c994f4055311aa7740aeb35a09ac2567d59296fb5e9398ba756be82466a36532df083831a4c39f9fc629a3d2166091fc0179ab3421bc3846fd129b9ea6ad2e09ca7bac85ced34d69430bddaafc6486c6f338cbf6d0b21fc4c470a86c3741aeaa6cd673d734fc66f563b7725d997ab7a42f79dce2bb9c4ab1129adc403eaa4b2b3d4dccf84b1fb10af33227a001e34e01ed506cbd857b9b30a2e48769fbe3beb5782bf134703b14b8da318fd0c841d7289e381def26a31570a5868ef4b8d7856433817f575e48d3bff7ae98bad1549234001ea1b23e2867517b39cec1f5754a31fbe24e5c932de31621f11dcf2c43f8f259139b56cc44a0c198a5db886096a46d7dbf3cfa509528eab60d06070a38a08729f8b54546b9394c6520d89967f9cd5efed6e1a93293c85f883e8975a330aa52e75f1b7fede98d78de8de18c9b40df8ca9d90ce00e0fb889bd24369035f5ba0dda0d2df880c4160f9a2c597650fb0d49579440fe397155e617c33f1b422aab221858ff0a6fe4a96beac38d17a36c723946bf5d4b5f42625b5eacdd3787e6136c68f9a0eab7d008d5beb9debd3fc3e3dde48d78edcffc41d64853580da10b3da85af46e7f79c8d1a95c9a04649"
               }
            ],
            "kernels":[
               {
                  "features":"Plain",
                  "fee":"800000",
                  "lock_height":"0",
                  "excess":"000000000000000000000000000000000000000000000000000000000000000000",
                  "excess_sig":"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
               }
            ]
         }
      },
      "amount":"10000000",
      "fee":"800000",
      "height":"1347224",
      "lock_height":"0",
      "participant_data":[
         {
            "id":"0",
            "public_blind_excess":"02bd340e78d158585073c568954780315e20c2b7e262b14ba3088c980f06c9f840",
            "public_nonce":"03d7fc24cb2ca46abde7884fd5c0e073ac8aa7457ab92f22b5b5558093d8543f7b",
            "part_sig":null,
            "message":"testing python",
            "message_sig":"2d6e041ec5b314fd5433fd6c22144f1feca9c12c248281c903afef7d5ebfbe41f53afc71932da0ff370c1c2c4bcfc8fb9abf7bd8d04bb55f56c6054b6b38c8c2"
         },
         {
            "id":"1",
            "public_blind_excess":"03ab414c89ee13d85cb760d5788010768108cf06a4e577706e872e8fcf8d59f12c",
            "public_nonce":"037f2ead110437263123550b89eec9e66f5dcbee1c71c05e81f9a0e4aab740cf25",
            "part_sig":"25cf40b7aae4a0f9815ec0711ceecb5d6fe6c9ee890b55233126370411ad2e7f622471235c2856c495f9b190e9fa455ce9f59d5d51fbd9687952ef28479988b9",
            "message":null,
            "message_sig":null
         }
      ]
   }
]
"""