import sat as sat
import sat_rotatin as sat_r

instance = 1

result = sat.run(instance)
if result is not None:
    print(result)
    sat.plot_result(result)
    sat.write_file(result)


# result = sat_r.run(instance)
# if result is not None:exit
#     print(result)
#     sat_r.plot_result(result)
#     sat_r.write_file(result)


# for i in range(1, 41):
#     print("this is instance {}".format(i))
#     result = sat.run(i)
#     if result is not None:
#         print(result)
#         sat.plot_result(result)
#         sat.write_file(result)

# for i in range(1, 41):
#     print("this is instance {}".format(i))
#     result = sat_r.run(i)
#     if result is not None:
#         print(result)
#         sat_r.plot_result(result)
#         sat_r.write_file(result)